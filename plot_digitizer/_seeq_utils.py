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
    'get_pltdgtz_property', 'get_selected_curve_points', 'get_available_asset_names_to_item_id_dict',
    'create_and_push_formula', 'modify_workstep'
)


PROPERTY_NAME = 'PltDgtz'

class NoParentAsset(Exception):
    def __init__(self, message):
        super().__init__(message)


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
    """Get the asset of an item (e.g. signal)"""
    try:
        tree = trees_api.get_tree(id=id)
        item = tree.item
        ancestors = item.ancestors
        return ancestors[-1]
    except IndexError:
        return None


def update_pltdgtz_property(
    asset:'seeq.sdk.models.item_preview_v1.ItemPreviewV1', 
    selected_points_df:'pandas.DataFrame', 
    curve_set:'str', curve_name:'str', 
    items_api:'seeq.sdk.apis.items_api.ItemsApi'):

    existing_pltdgtz = get_pltdgtz_property(asset, items_api)

    stringified_selected_points = stringify_selected_points(selected_points_df)

    if existing_pltdgtz is None:
        value = {curve_set:{curve_name:stringified_selected_points}}
        value = curvesets_to_json(value)
    else:
        current_value = json_to_curvesets(existing_pltdgtz.value)
        try:
            curve_set_dict = current_value[curve_set]
            curve_set_dict.update({curve_name: stringified_selected_points})
        except KeyError:
            current_value.update({curve_set:{curve_name: stringified_selected_points}})

        value = curvesets_to_json(current_value)

    body = sdk.PropertyInputV1(
        unit_of_measure='string', value=value
    )
    items_api.set_property(id=asset.id, property_name=PROPERTY_NAME, body=body)
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

def get_selected_curve_points(asset:'{str, seeq.sdk.models.item_preview_v1.ItemPreviewV1}', 
                              curve_set:'str', curve_name:'str', 
                              items_api:'seeq.sdk.apis.items_api.ItemsApi', delimiter='||'):

    prop = get_pltdgtz_property(asset, items_api)
    if prop is None:
        raise NameError(
            'No property corresponding to curve_set={}, curve_name={} in asset with id {}'.format(
                curve_set, curve_name, asset
            )
        )
    curve_sets_dict = json_to_curvesets(prop.value)

    return destringify_points(curve_sets_dict[curve_set][curve_name])


def get_available_asset_names_to_item_id_dict(
    worksheet:'seeq.spy.workbooks._worksheet.AnalysisWorksheet',
    trees_api:'seeq.sdk.apis.trees_api.TreesApi') -> 'dict':
    """after calling get_available_asset_names_to_item_id_dict(worksheet), use the returned dict value in get_asset()"""

    available_asset_names_to_item_id = dict()

    for item_id in worksheet.display_items.ID.values:
        asset = get_asset(item_id, trees_api)
        if asset is None:
            continue
        available_asset_names_to_item_id.update({asset.name:item_id})
        
        if len(available_asset_names_to_item_id) == 0:
            raise NoParentAsset('No items with parent assets in worksheet.')

    return available_asset_names_to_item_id

def create_and_push_formula(
    curve_set:'str', curve_name:'str', asset_id:'str', 
    auth_token:'str', x_axis_id:'str', quiet:'bool'=True):
    
    signal_notator = '$a'
    curveSet = curve_set
    curveName = curve_name
    authToken = auth_token
    assetId = asset_id

    signal_notator_to_id_dict = {signal_notator:x_axis_id}

    # formula name
    formula_name = '{}, {}'.format(curveSet, curveName)
    
    formula_formatter = """PlotDigitizer_Show({}, 
    "{}".toSignal(), 
    "{}".toSignal(), 
    "{}".toSignal(), 
    "{}".toSignal())"""
    
    formula_string = formula_formatter.format(signal_notator, assetId, curveSet, curveName, authToken)
    
    body={
        'Name':formula_name, 
        'Formula':formula_string,
        'Formula Parameters':signal_notator_to_id_dict, 
        'Type':'Signal',
    }

    bodies = [body]

    metatag = pd.DataFrame(bodies)
    
    results = spy.push(metadata=metatag, workbook=None, worksheet=None, quiet=quiet)
    return results

def duplicate_current_workstep_data(workstep:'seeq.spy.workbooks._workstep.AnalysisWorkstep')->'dict':
    """Return a copy of the workstep data dict"""
    version = workstep.data['version']
    existing_stores = workstep.get_workstep_stores()
    stores_str = json.dumps(existing_stores)
    new_stores = json.loads(stores_str)
    return {'version':version, 'state':{'stores':new_stores}}

def add_series_to_workstep_stores(workstep_stores:'dict', id:'str', name:'str'):
    workstep_stores['sqTrendSeriesStore']['items'].append({'id':id, 'name':name})
    return

def modify_workstep(
    workbook:'seeq.spy.workbooks._workbook.Analysis',
    worksheet:'seeq.spy.workbooks._worksheet.AnalysisWorksheet',
    formula_push_results:'pandas.DataFrame',
    trees_api:'seeq.sdk.apis.trees_api.TreesApi',
    workbooks_api:'seeq.sdk.apis.workbooks_api.WorkbooksApi',
    x_range:'tuple', y_range:'tuple'):
    old_display = worksheet.display_items[['Name', 'ID', 'Type']].copy()
    
    # TODO: FIX XAXIS ID
    try:
        x_axis_id = old_display.iloc[0].ID
        y_axis_id = old_display.iloc[1].ID
    except IndexError:
        raise IndexError('Must have at least two signals on the screen')
    asset_id = get_asset(x_axis_id, trees_api=trees_api).id
    
    # get formula parameters
    formula_name = formula_push_results.iloc[0].Name
    formula_id = formula_push_results.iloc[0].ID
    
    # specify items to add to display
#     add_display = pd.DataFrame(
#         dict(
#             Name=formula_name, 
#             ID=formula_id,
#             Type='Signal'
#         ), 
#         index=[0]
#     )
    
    # update display items
#     new_display_items = pd.concat(
#         (old_display, add_display)
#     ).reset_index(drop=True)
    
#     worksheet.display_items = new_display_items
    
    # get the current workstep and stores for updating
    current_workstep = worksheet.current_workstep()
#     workstep_data = current_workstep.data.copy()
#     stores = workstep_data['state']['stores']
    workstep_data = duplicate_current_workstep_data(current_workstep)
#     stores = current_workstep.get_workstep_stores()
    stores = workstep_data['state']['stores']
    add_series_to_workstep_stores(stores, id=formula_id, name=formula_name)
    
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
    if existing_x_range[0] is None or existing_x_range[1] is None:
        existing_x_range = (np.inf, -np.inf)

    if view_region['ys'] == {}:
        existing_y_range = (np.inf, -np.inf)
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
    
    fx_lines = stores['sqScatterPlotStore']['fxLines']
    fx_lines.append({'id': formula_id, 'color':'#000000'})
    
    # update f(x)
    stores['sqScatterPlotStore'].update({
        'fxLines': fx_lines
    })

    # push results
#     print(workstep_data)
    payload = dict(data=json.dumps(workstep_data))
    response = workbooks_api.create_workstep(workbook_id=workbook.id, worksheet_id=worksheet.id, body=payload)
    out = workbooks_api.set_current_workstep(workbook_id=workbook.id, worksheet_id=worksheet.id, workstep_id=response.id)
#     workbook.push()
    return 

