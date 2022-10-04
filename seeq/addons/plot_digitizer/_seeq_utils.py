import pandas as pd
import numpy as np

from seeq import spy, sdk
import json

from ._utils import (
    stringify_selected_points, destringify_points,
    curvesets_to_json, json_to_curvesets
)


__all__ = (
    'get_workbook', 'get_worksheet', 'get_asset', 'update_pltdgtz_property',
    'get_pltdgtz_property', 'get_available_asset_names_to_item_id_dict',
    'create_and_push_formula', 'modify_workstep', 'get_plot_digitizer_storage_id',
    'get_plot_digitizer_storage_dict', 'NoParentAsset', 'add_item_to_asset',
    'update_plot_digitizer_storage', 'delete_empty_plot_digitizer_storage',
    'create_scalar', 'format_time_stamp_for_seeq_capsule', 'create_seeq_formula',
    'get_curve_set_asset_id'
)


PROPERTY_NAME = 'PltDgtz'

class NoParentAsset(Exception):
    def __init__(self, message):
        super().__init__(message)

        
def create_asset(name, assets_api):
    response = assets_api.create_asset(
        body={
            "name":name
        }
    )
    return response

def get_existing_curve_set_asset_id(parent_asset_id:'str', curve_set_name:'str', trees_api):
    """return None if curve set does not exist, otherwise return the id of that curve set asset"""
    parent_tree = trees_api.get_tree(id=parent_asset_id)
    exisiting_curve_set_asset_id = None
    for child in parent_tree.children:
        if curve_set_name == child.name:
            if child.type == 'Asset':
                exisiting_curve_set_asset_id = child.id
                break
            else:
                raise TypeError(
                    'A child of parent asset id {} exists with name {}, but is not an Asset. Is instead type {}'.format(parent_asset_id, curve_set_name, child.type)
                )
                break
        else:
            continue
            
    return exisiting_curve_set_asset_id



def get_curve_set_asset_id(parent_asset_id, curve_set_name, trees_api, assets_api):
    # check if name already exists under parent asset
    existing_curve_set_asset_id = get_existing_curve_set_asset_id(parent_asset_id, curve_set_name, trees_api)

    if existing_curve_set_asset_id is None:

        # create the asset
        asset_creation_response = create_asset(curve_set_name, assets_api)
        # move the asset under parent id
        add_item_to_asset(parent_asset_id, curve_set_name, asset_creation_response.id, trees_api, overwrite=False)

        existing_curve_set_asset_id = asset_creation_response.id
        
    return existing_curve_set_asset_id

def get_workbook(wkb_id:'str', quiet=True):
    workbook = spy.workbooks.pull(
        spy.workbooks.search(
            {'ID':wkb_id}, quiet=quiet
        ), 
        quiet=quiet
    )[0]
    return workbook

def get_worksheet(workbook:'seeq.spy.workbooks._workbook.Analysis', wks_id:'str'):
    wks = None
    for worksheet in workbook.worksheets:
        if worksheet.id == wks_id:
            wks = worksheet
            break
    return wks

def get_asset(
    id:'str', trees_api:'seeq.sdk.apis.trees_api.TreesApi'
) -> 'seeq.sdk.models.item_preview_v1.ItemPreviewV1':
    """Get the parent asset of an item (e.g. signal)"""
    try:
        tree = trees_api.get_tree(id=id)
        item = tree.item
        ancestors = item.ancestors
        return ancestors[-1]
    except IndexError:
        return None
    
def create_scalar(name, formula, scalars_api)->'seeq.sdk.models.calculated_item_output_v1.CalculatedItemOutputV1':
    body = sdk.ScalarInputV1(name=name, formula=formula, unit_of_measure='string')
    returned = scalars_api.create_calculated_scalar(body=body)
    return returned

def get_scalar(id:'str', scalars_api:'seeq.sdk.apis.scalars_api.ScalarsApi'):
    return scalars_api.get_scalar(id=id)

def get_plot_digitizer_storage_dict(
    scalar:'{str, seeq.sdk.models.calculated_item_output_v1.CalculatedItemOutputV1}',
    scalars_api:'seeq.sdk.apis.scalars_api.ScalarsApi')->'dict':
    if type(scalar) is str:
        scalar = get_scalar(id=scalar, scalars_api=scalars_api)
        
    starter = scalar.formula[0]
    return json.loads(scalar.formula.replace(starter, ""))

def update_scalar_formula(
    scalar:'{str, seeq.sdk.models.calculated_item_output_v1.CalculatedItemOutputV1}',
    formula:'str',
    scalars_api:'seeq.sdk.apis.scalars_api.ScalarsApi'):
    
    if type(scalar) is str:
        scalar = get_scalar(scalar, scalars_api)
    
    body = {
      "datasourceClass": scalar.datasource_class,
      "scalars": [
        {
          "datasourceClass": scalar.datasource_class,
          "dataId": scalar.data_id,
          "datasourceId": scalar.datasource_id,
          "name": scalar.name,
          "formula": formula
        }
      ],
      "datasourceId": scalar.datasource_id
    }
    
    returned = scalars_api.put_scalars(
        body=body
    )
    return returned

def get_plot_digitizer_storage_id(asset_id:'str', 
                                  scalars_api:'seeq.sdk.apis.scalars_api.ScalarsApi',
                                  REGION_OF_INTEREST:'bool', delete_empty=True,
                                  quiet=True)->'str':
    if not REGION_OF_INTEREST:
        # original case of simple plot digitization
        name = '{}.PlotDigitizerScalarStorage'.format(asset_id)
        search_results = spy.search({'Name':name, 'Type':'Scalar'}, quiet=quiet)
    else:
        # region of interest case
        name = '{}.PlotDigitizerROIStorage'.format(asset_id)
        search_results = spy.search({'Name':name, 'Type':'Scalar'}, quiet=quiet)
        
    
    if len(search_results) == 1:
        _id = search_results.ID.iloc[0]
    elif len(search_results) == 0:
        # create the condition
        create_return = create_scalar(
            name=name,
            formula="'{}'".format(json.dumps({})),
            scalars_api=scalars_api
        )
        _id = create_return.id
    else:
        if delete_empty:
            
            delete_empty_plot_digitizer_storage(search_results, scalars_api)
            return get_plot_digitizer_storage_id(
                asset_id, scalars_api, REGION_OF_INTEREST, delete_empty=False, quiet=quiet
            )
        
        raise Exception("Multiple Plot digitizer storage scalars with id {}".format(asset_id))
    
    return _id

def update_plot_digitizer_storage(updater_dict:'dict', storage_id:'str', 
                                  scalars_api:'seeq.sdk.apis.scalars_api.ScalarsApi'):
    # get the existing one, if None, create
    scalar = get_scalar(storage_id, scalars_api)
    existing = get_plot_digitizer_storage_dict(storage_id, scalars_api)
    
    for key, v in updater_dict.items():
        if key in existing:
            existing[key].update(v)
        else:
            existing.update({key:v})
    out = update_scalar_formula(
        scalar, 
        "'{}'".format(
            json.dumps(existing)
        ), 
        scalars_api
    )
        
    return out


def update_pltdgtz_property(
    storage_id:'str', 
    selected_points_df:'pandas.DataFrame', 
    curve_set:'str', curve_name:'str', 
    scalars_api:'seeq.sdk.apis.scalars_api.ScalarsApi'):

    stringified_selected_points = stringify_selected_points(selected_points_df)
    updater_dict = {curve_set:{curve_name:stringified_selected_points}}
    update_plot_digitizer_storage(updater_dict, storage_id, scalars_api)
    
    return 

def get_pltdgtz_property(
    asset:'{str, seeq.sdk.models.item_preview_v1.ItemPreviewV1}', 
    items_api:'seeq.sdk.apis.items_api.ItemsApi'):

    if type(asset) is str:
        all_properties = items_api.get_item_and_all_properties(id=asset).properties
    else:
        all_properties = items_api.get_item_and_all_properties(id=asset.id).properties
    for p in all_properties:
        if p.name != PROPERTY_NAME:
            continue
        return p

    return None


def get_available_asset_names_to_item_id_dict(
    worksheet:'seeq.spy.workbooks._worksheet.AnalysisWorksheet',
    trees_api:'seeq.sdk.apis.trees_api.TreesApi') -> 'dict':

    available_asset_names_to_item_id = dict()

    for item_id in worksheet.display_items.ID.values:
        asset = get_asset(item_id, trees_api)
        if asset is None:
            continue
        available_asset_names_to_item_id.update({asset.name:asset.id})
        
        if len(available_asset_names_to_item_id) == 0:
            raise NoParentAsset('No items with parent assets in worksheet.')

    return available_asset_names_to_item_id

def create_seeq_formula(
    name:'str', formula:'str', parameters:'dict', 
    formula_type:'str'='Signal', quiet:'bool'=True,
    workbook=None, worksheet=None)->'pd.DataFrame':
    body={
        'Name':name, 
        'Formula':formula,
        'Formula Parameters':parameters, 
        'Type':formula_type,
    }

    bodies = [body]

    metatag = pd.DataFrame(bodies)

    results = spy.push(metadata=metatag, workbook=workbook, worksheet=worksheet, quiet=quiet)
    return results

def format_time_stamp_for_seeq_capsule(timestamp:'str')->'str':
    ts = timestamp
    utc_offset = ts.utcoffset()
    seconds = utc_offset.seconds
    hours = int(np.floor(seconds/3600))
    if hours >= 0:
        hours = '+'+str(hours)
    else:
        hours = str(hours)

    if len(hours.replace('-','').replace('+','')) == 1:
        hours = hours[0] + '0' + hours[1]
    minutes = str(int(abs(np.floor(np.mod(seconds, -3600) / 60))))

    if len(minutes) == 1:
        minutes = '0' + minutes
        
    return ts.strftime("%Y-%m-%dT%H:%M:%S{}:{}").format(
        hours, minutes
    )

def create_and_push_formula(
    curve_set:'str', curve_name:'str', storage_id:'str', x_axis_id:'str', REGION_OF_INTEREST:'bool', 
    interpolation_method:'str ("linear", "cubic")'='cubic', y_axis_id:'str'=None, quiet:'bool'=True)->'pd.DataFrame':
    
    if not REGION_OF_INTEREST:
        # generate the first formula to pass the plot digitizer storage to external calc
        template = """$pdz.toSignal()"""

        signal_notator = '$x'
        curveSet = curve_set
        curveName = curve_name

        signal_notator_to_id_dict = {signal_notator:x_axis_id, '$pdz':storage_id}

        # formula name
        formula_name = '{}: {}'.format(curveSet, curveName)

        if interpolation_method == 'cubic':

            formula_formatter = """PltDgz_ShowCubic({}, {}, 
    "{}".toSignal(), 
    "{}".toSignal()
)"""
        elif interpolation_method == 'linear':
            formula_formatter = """PltDgz_ShowLinear({}, {}, 
    "{}".toSignal(), 
    "{}".toSignal()
)"""
        else:
            raise ValueError('interpolation_method {} not allowed. Allowed values are "linear" and "cubic"'.format(interpolation_method))

        formula_string = formula_formatter.format(signal_notator, template, curveSet, curveName)
        
        results = create_seeq_formula(formula_name, formula_string, signal_notator_to_id_dict)

        return results
    
    else:
        if y_axis_id is None:
            raise TypeError('No yaxis id supplied')
        # generate the first formula to pass the plot digitizer storage to external calc
        template = """$pdz.toSignal()"""

        xsignal_notator = '$x'
        ysignal_notator = '$y'
        curveSet = curve_set
        curveName = curve_name

        signal_notator_to_id_dict = {xsignal_notator:x_axis_id, ysignal_notator:y_axis_id, '$pdz':storage_id}

        # formula name
        formula_name = '{}: {} (ROI)'.format(curveSet, curveName)

        formula_formatter = """PltDgz_ROI({}, {}, {},
    "{}".toSignal(), 
    "{}".toSignal()
).toCondition()"""

        formula_string = formula_formatter.format(xsignal_notator, ysignal_notator, template, curveSet, curveName)

        body={
            'Name':formula_name, 
            'Formula':formula_string,
            'Formula Parameters':signal_notator_to_id_dict, 
            'Type': 'Condition'
        }

        bodies = [body]

        metatag = pd.DataFrame(bodies)

        results = spy.push(metadata=metatag, workbook=None, worksheet=None, quiet=quiet)
        return results
    
def add_item_to_asset(asset_id:'str', item_name:'str', item_id:'str', 
                      trees_api:'seeq.sdk.apis.trees_api.TreesApi',
                      overwrite:'bool'=True
                     ):
    
    if overwrite:
        
        # check for same names that already exist
        tree = trees_api.get_tree(id=asset_id)
        existing_ids_of_same_name = []
        for child in tree.children:
            if child.name == item_name:
                existing_ids_of_same_name.append(child.id)
                
        # remove existing
        for _id in existing_ids_of_same_name:
            trees_api.remove_node_from_tree(id=_id)
    
    trees_api.move_nodes_to_parent(
        parent_id=asset_id, 
        body=sdk.ItemIdListInputV1(
            items=[item_id]
        )
    )
    
    return

def duplicate_current_workstep_data(workstep:'seeq.spy.workbooks._workstep.AnalysisWorkstep')->'dict':
    """Return a copy of the workstep data dict"""
    version = workstep.data['version']
    existing_stores = workstep.get_workstep_stores()
    stores_str = json.dumps(existing_stores)
    new_stores = json.loads(stores_str)
    return {'version':version, 'state':{'stores':new_stores}}

def find_lane_for_yaxis_id(y_axis_id:'str', items:'[dict]'):
    for item in items:
        if item['id'] == y_axis_id:
            return item['lane']
        
    raise ValueError('Cannot find y_axis_id {} in workstep stores.'.format(y_axis_id))

def add_series_to_workstep_stores(workstep_stores:'dict', id:'str', name:'str', lane:'int'=None):
    if lane is None:
        workstep_stores['sqTrendSeriesStore']['items'].append({'id':id, 'name':name})
    else:
        workstep_stores['sqTrendSeriesStore']['items'].append({'id':id, 'name':name, 'lane':lane})
    return

def add_condition_to_workstep_stores(workstep_stores:'dict', id:'str', name:'str'):
    workstep_stores['sqTrendCapsuleSetStore']['items'].append({'id':id, 'name':name})
    return

def delete_empty_plot_digitizer_storage(
    storage_search_results:'pd.DataFrame', scalars_api:'seeq.sdk.apis.scalars_api.ScalarsApi'
)->'str':
    for _id in storage_search_results.ID.values:
        tdict = get_plot_digitizer_storage_dict(_id, scalars_api)
        if tdict == {}:
            delete_scalar(_id, scalars_api)
    return

def merge_plot_digitizer_storage_dicts(existing, new):
    """Any matching keys at the curve set level will be updated with '_vX' at the end."""
    clashing_keys = set(existing.keys()).intersection(set(new.keys()))
    for key in clashing_keys:
        existing.update({'{}_v1'.format(key):existing.pop(key)})
        existing.update({'{}_v2'.format(key):new.pop(key)})

    existing.update(new)
    return existing

def delete_scalar(ID:'str', scalars_api:'seeq.sdk.apis.scalars_api.ScalarsApi'):
    scalars_api.archive_scalar(id=ID)
    return

def aggregate_existing_plot_digitizer_storages(
    storage_search_results:'pd.DataFrame', scalars_api:'seeq.sdk.apis.scalars_api.ScalarsApi'
)->'str':
    """For each ID in storage search results, aggregate their dictionaries.
    Any matching keys AT THE CURVE SET level will be updated with '_vX' at the end.
    Delete all but final ID, update plot digitizer storage on the final ID
    """
    
    # merge existing dicts:
    out = {}
    for _id in storage_search_results.ID.values:
        tdict = get_plot_digitizer_storage_dict(_id, scalars_api)
        out = merge_plot_digitizer_storage_dicts(out, tdict)
        
    # delete all but last id:
    for _id in storage_search_results.ID.values[:-1]:
        delete_scalar(_id, scalars_api)
    
    out_id = storage_search_results.ID.values[-1]
    update_plot_digitizer_storage(out, out_id, scalars_api)
    
    return out_id

def get_maxmin_XY_signals(
    x_id:'str', y_id:'str', 
    display_range:'dict<"Start":Timestamp, "End":Timestamp,>',
    quiet=True)->'pd.DataFrame':
    df = spy.pull(
        pd.DataFrame(
            {
                'ID':[x_id, y_id], 
                'Type':['Signal', 'Signal']
            }
        ), 
        start=display_range['Start'],
        end=display_range['End'],
        quiet=quiet
    ).describe()
    renamer = {
        name:_id for name, _id in zip(list(df.columns), [x_id, y_id])
    }
    
    return df.loc[['min', 'max']].rename(columns=renamer)

def modify_workstep(
    workbook:'seeq.spy.workbooks._workbook.Analysis',
    worksheet:'seeq.spy.workbooks._worksheet.AnalysisWorksheet',
    formula_push_results:'pandas.DataFrame',
    trees_api:'seeq.sdk.apis.trees_api.TreesApi',
    workbooks_api:'seeq.sdk.apis.workbooks_api.WorkbooksApi',
    x_range:'tuple', y_range:'tuple', x_axis_id:'str', y_axis_id:'str',
    REGION_OF_INTEREST:'bool'):
    
    old_display = worksheet.display_items[['Name', 'ID', 'Type']].copy()
    
    
    # get formula parameters
    formula_name = formula_push_results.iloc[0].Name
    formula_id = formula_push_results.iloc[0].ID

    
    # get the current workstep and stores for updating
    current_workstep = worksheet.current_workstep()
    workstep_data = duplicate_current_workstep_data(current_workstep)
    stores = workstep_data['state']['stores']
    if REGION_OF_INTEREST:
        add_condition_to_workstep_stores(stores, id=formula_id, name=formula_name)
    else:
        lane = find_lane_for_yaxis_id(y_axis_id, stores['sqTrendSeriesStore']['items'])
        add_series_to_workstep_stores(stores, id=formula_id, name=formula_name, lane=lane)
    
    # update scatter plot
    xSignal_dict = stores['sqScatterPlotStore']['xSignal']
    if xSignal_dict is None:
        xSignal_dict = {'id':x_axis_id}
    else:
        xSignal_dict.update({'id':x_axis_id})


    stores['sqScatterPlotStore'].update(
        {'ySignals':[{'id': y_axis_id, 'formatOptions': {}}]}
    )
    
    # put in scatter plot view
    stores['sqWorksheetStore'].update({'viewKey':'SCATTER_PLOT'})
    
    # set the view region
    view_region = stores['sqScatterPlotStore']['viewRegion']

    existing_x_range = (view_region['x']['min'], view_region['x']['max'])

    # case where no scatter plot has yet been established
    if (existing_x_range[0] is None) or (existing_x_range[1] is None):
        minmaxdf = get_maxmin_XY_signals(x_axis_id, y_axis_id, current_workstep.display_range)
        existing_x_range = tuple(minmaxdf[x_axis_id].values)

    if view_region['ys'] == {}:
        try:
            existing_y_range = tuple(minmaxdf[y_axis_id].values)
        except NameError:
            minmaxdf = get_maxmin_XY_signals(x_axis_id, y_axis_id, current_workstep.display_range)
            existing_y_range = tuple(minmaxdf[y_axis_id].values)
    else:
        y_view_key = list(view_region['ys'].keys())[0]
        existing_y_range = (view_region['ys'][y_view_key]['min'], view_region['ys'][y_view_key]['max']) 
        
    x_min, x_max = x_range
    y_min, y_max = y_range

    stores['sqScatterPlotStore'].update(
        {
            'viewRegion':{
                'x': {
                    'min': min(x_min, existing_x_range[0]), 
                    'max': max(x_max, existing_x_range[1])
                }, 
                'ys': {
                    y_axis_id: {
                        'min': min(y_min, existing_y_range[0]), 
                        'max': max(y_max, existing_y_range[1])
                    }
                }
            }
        }
    )
    
    if not REGION_OF_INTEREST:
        fx_lines = stores['sqScatterPlotStore']['fxLines']
        fx_lines.append({'id': formula_id, 'color':'#000000'})

        # update f(x)
        stores['sqScatterPlotStore'].update({
            'fxLines': fx_lines
        })
    else:
        stores['sqScatterPlotStore']['colorConditionIds'].append(formula_id)

    # push results
#     print(workstep_data)
    payload = dict(data=json.dumps(workstep_data))
    response = workbooks_api.create_workstep(workbook_id=workbook.id, worksheet_id=worksheet.id, body=payload)
    out = workbooks_api.set_current_workstep(workbook_id=workbook.id, worksheet_id=worksheet.id, workstep_id=response.id)
#     workbook.push()
    return 

