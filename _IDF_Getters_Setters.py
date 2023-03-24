import datetime, sys, os

def get_zone_handles(state):
    global zone_names
    zone_names = ['Basement',
                  'Core_bottom',
                  'Core_mid',
                  'Core_top',
                  'Perimeter_bot_ZN_1',
                  'Perimeter_bot_ZN_2',
                  'Perimeter_bot_ZN_3',
                  'Perimeter_bot_ZN_4',
                  'Perimeter_mid_ZN_1',
                  'Perimeter_mid_ZN_2',
                  'Perimeter_mid_ZN_3',
                  'Perimeter_mid_ZN_4',
                  'Perimeter_top_ZN_1',
                  'Perimeter_top_ZN_2',
                  'Perimeter_top_ZN_3',
                  'Perimeter_top_ZN_4']
    '''
    OutputVariable	Zone Air Terminal VAV Damper Position	BASEMENT VAV BOX COMPONENT
    OutputVariable	Zone Air System Sensible Heating Energy	BASEMENT	
    #Actuator	System Node Setpoint	Mass Flow Rate Setpoint	BASEMENT VAV BOX DAMPER NODE;
    Actuator	System Node Setpoint	Mass Flow Rate Setpoint	BASEMENT VAV BOX OUTLET NODE NAME;
    '''
    zone_temp_c = []
    zone_target_heat_temp_c = []
    zone_target_cool_temp_c = []
    zone_damper_pos_sensor = []
    zone_damper_pos_actuator = []
    zone_damper_act_des_heat_mass_flow = []
    zone_damper_act_des_cool_mass_flow = []
    for zone in zone_names:
        _tmpRtemp = ep_api.exchange.get_variable_handle(state,
                                                   "Zone Air Temperature",
                                                   zone)
        _tmpTtempHeat = ep_api.exchange.get_variable_handle(state,
                                                   "Zone Thermostat Heating Setpoint Temperature",
                                                   zone)
        _tmpTtempCool = ep_api.exchange.get_variable_handle(state,
                                                    "Zone Thermostat Cooling Setpoint Temperature",
                                                    zone)
        _tmpDPosSensor = ep_api.exchange.get_variable_handle(state,
                                                    "Zone Air Terminal VAV Damper Position",
                                                    zone+" VAV BOX COMPONENT")
        #Final Zone Design Cooling Air Mass Flow Rate
        _tmpDesHetMassFlow = ep_api.exchange.get_internal_variable_handle(state,
                                                    "Final Zone Design Heating Air Mass Flow Rate",
                                                    zone)
        _tmpDesCoolMassFlow = ep_api.exchange.get_internal_variable_handle(state,
                                                    "Final Zone Design Cooling Air Mass Flow Rate",
                                                    zone)
        _tmpDPosActuator = ep_api.exchange.get_actuator_handle(state,
                                                    "System Node Setpoint",
                                                    "Mass Flow Rate Setpoint",
                                                    zone+" VAV BOX OUTLET NODE NAME")

        if _tmpRtemp * _tmpTtempHeat * _tmpTtempCool * _tmpDPosSensor * _tmpDPosActuator * \
            _tmpDesHetMassFlow * _tmpDesCoolMassFlow < 0:
            raise Exception("Error: Invalid handle for zone: "+zone)
        zone_temp_c.append(_tmpRtemp)
        zone_target_heat_temp_c.append(_tmpTtempHeat)
        zone_target_cool_temp_c.append(_tmpTtempCool)
        zone_damper_pos_sensor.append(_tmpDPosSensor)
        zone_damper_pos_actuator.append(_tmpDPosActuator)
        zone_damper_act_des_heat_mass_flow.append(_tmpDesHetMassFlow)
        zone_damper_act_des_cool_mass_flow.append(_tmpDesCoolMassFlow)

    return zone_temp_c, zone_target_heat_temp_c, zone_target_cool_temp_c, \
        zone_damper_pos_sensor, zone_damper_pos_actuator, \
        zone_damper_act_des_heat_mass_flow, zone_damper_act_des_cool_mass_flow

def get_building_handles(state):
    global allHandles
    allHandles = {}
    allHandles['sensor'] = {}
    allHandles['actuator'] = {}

    oat_c = ep_api.exchange.get_variable_handle(state,"Site Outdoor Air Drybulb Temperature",
                                                                             "Environment")
    rh_percent = ep_api.exchange.get_variable_handle(state,"Site Outdoor Air Humidity Ratio",
                                                                             "Environment")
    waterTemp = ep_api.exchange.get_variable_handle(state,"Site Mains Water Temperature",
                                                                             "Environment")
    hvac_electricity = ep_api.exchange.get_variable_handle(state,"Facility Total HVAC Electricity Demand Rate",
                                                                                "WHOLE BUILDING")
    chiler1_set_c_sensor = ep_api.exchange.get_variable_handle(state,
                                                       "Chiller Evaporator Outlet Temperature",
                                                       "COOLSYS1 CHILLER 1")
    chiler2_set_c_sensor = ep_api.exchange.get_variable_handle(state,
                                                         "Chiller Evaporator Outlet Temperature",
                                                         "COOLSYS1 CHILLER 2")
    boiler_set_c_sensor = ep_api.exchange.get_variable_handle(state,
                                                         "Boiler Outlet Temperature",
                                                         "HEATSYS1 BOILER")
    chiler1_set_c_actuator = ep_api.exchange.get_actuator_handle(state,
                                                        "System Node Setpoint",
                                                        "Temperature Setpoint",
                                                        "COOLSYS1 SUPPLY EQUIPMENT OUTLET NODE 1")
    chiler2_set_c_actuator = ep_api.exchange.get_actuator_handle(state,
                                                        "System Node Setpoint",
                                                        "Temperature Setpoint",
                                                        "COOLSYS1 SUPPLY EQUIPMENT OUTLET NODE 2")
    boiler_set_c_actuator = ep_api.exchange.get_actuator_handle(state,
                                                        "System Node Setpoint",
                                                        "Temperature Setpoint",
                                                        "HEATSYS1 SUPPLY EQUIPMENT OUTLET NODE")
    odb_actuator_handle = ep_api.exchange.get_actuator_handle(state,
                                                              "Weather Data", "Outdoor Dry Bulb", "Environment")
    orh_actuator_handle = ep_api.exchange.get_actuator_handle(state,
                                                              "Weather Data", "Outdoor Relative Humidity", "Environment")
    #find if any of hanldes < -1, then raise exception
    _allHandles = [oat_c, rh_percent, waterTemp, hvac_electricity,
                   chiler1_set_c_sensor, chiler2_set_c_sensor, boiler_set_c_sensor,
                     chiler1_set_c_actuator, chiler2_set_c_actuator, boiler_set_c_actuator,
                        odb_actuator_handle, orh_actuator_handle]
    if any([x < 0 for x in _allHandles]):
        raise Exception("Error: Invalid handle")

    zone_temp_c, zone_target_heat_temp_c, zone_target_cool_temp_c, \
        zone_damper_pos_sensor, zone_damper_pos_actuator,\
        zone_damper_act_des_heat_mass_flow, zone_damper_act_des_cool_mass_flow = \
        get_zone_handles(state)

    allHandles['sensor']['hvac_electricity_watts'] = hvac_electricity
    allHandles['sensor']['room_temp_c'] = zone_temp_c
    allHandles['sensor']['Chiler1_SET_C'] = chiler1_set_c_sensor
    allHandles['sensor']['Chiler2_SET_C'] = chiler2_set_c_sensor
    allHandles['sensor']['Boiler_SET_C'] = boiler_set_c_sensor
    allHandles['sensor']['Damper_Position'] = zone_damper_pos_sensor
    allHandles['sensor']['OAT_C'] = oat_c
    allHandles['sensor']['RH_percent'] = rh_percent
    allHandles['sensor']['siteWaterTemp'] = waterTemp
    allHandles['sensor']['room_target_heat_temp_c'] = zone_target_heat_temp_c
    allHandles['sensor']['room_target_cool_temp_c'] = zone_target_cool_temp_c
    allHandles['sensor']['room_damper_des_heat_mass_flow_kg_per_s'] = zone_damper_act_des_heat_mass_flow
    allHandles['sensor']['room_damper_des_cool_mass_flow_kg_per_s'] = zone_damper_act_des_cool_mass_flow

    allHandles['actuator']['Chiler1_SET_C'] = chiler1_set_c_actuator
    allHandles['actuator']['Chiler2_SET_C'] = chiler2_set_c_actuator
    allHandles['actuator']['Boiler_SET_C'] = boiler_set_c_actuator
    allHandles['actuator']['Damper_Position'] = zone_damper_pos_actuator
    allHandles['actuator']['OAT_C'] = odb_actuator_handle
    allHandles['actuator']['RH_percent'] = orh_actuator_handle
def get_sensor_value(state):
    time_in_hours = ep_api.exchange.current_sim_time(state)
    _readable_time = datetime.timedelta(hours=time_in_hours)
    print('Time: ', _readable_time)
    sensor_values = {}
    sensor_values['hvac_electricity_watts'] = ep_api.exchange.get_variable_value(state,
                                                                           allHandles['sensor']['hvac_electricity_watts'])
    sensor_values['room_temp_c'] = []
    for i in range(len(allHandles['sensor']['room_temp_c'])):
        sensor_values['room_temp_c'].append(
            ep_api.exchange.get_variable_value(state, allHandles['sensor']['room_temp_c'][i]))
    sensor_values['Chiler1_SET_C'] = ep_api.exchange.get_variable_value(state, allHandles['sensor']['Chiler1_SET_C'])
    sensor_values['Chiler2_SET_C'] = ep_api.exchange.get_variable_value(state, allHandles['sensor']['Chiler2_SET_C'])
    sensor_values['Boiler_SET_C'] = ep_api.exchange.get_variable_value(state, allHandles['sensor']['Boiler_SET_C'])
    sensor_values['Damper_Position'] = []
    for i in range(len(allHandles['sensor']['Damper_Position'])):
        sensor_values['Damper_Position'].append(
            ep_api.exchange.get_variable_value(state, allHandles['sensor']['Damper_Position'][i]))
    sensor_values['OAT_C'] = ep_api.exchange.get_variable_value(state, allHandles['sensor']['OAT_C'])
    sensor_values['RH_percent'] = ep_api.exchange.get_variable_value(state, allHandles['sensor']['RH_percent'])
    sensor_values['room_target_heat_temp_c'] = []
    sensor_values['room_target_cool_temp_c'] = []
    sensor_values['room_damper_des_heat_mass_flow_kg_per_s'] = []
    sensor_values['room_damper_des_cool_mass_flow_kg_per_s'] = []
    for i in range(len(allHandles['sensor']['room_target_heat_temp_c'])):
        sensor_values['room_target_heat_temp_c'].append(
            ep_api.exchange.get_variable_value(state, allHandles['sensor']['room_target_heat_temp_c'][i]))
        sensor_values['room_target_cool_temp_c'].append(
            ep_api.exchange.get_variable_value(state, allHandles['sensor']['room_target_cool_temp_c'][i]))
        sensor_values['room_damper_des_heat_mass_flow_kg_per_s'].append(
            ep_api.exchange.get_variable_value(state, allHandles['sensor']['room_damper_des_heat_mass_flow_kg_per_s'][i]))
        sensor_values['room_damper_des_cool_mass_flow_kg_per_s'].append(
            ep_api.exchange.get_variable_value(state, allHandles['sensor']['room_damper_des_cool_mass_flow_kg_per_s'][i]))

    return sensor_values
def set_actuators(state, to_set):
    ep_api.exchange.set_actuator_value(state, allHandles['actuator']['Chiler1_SET_C'], to_set['Chiler1_SET_C'])
    ep_api.exchange.set_actuator_value(state, allHandles['actuator']['Chiler2_SET_C'], to_set['Chiler2_SET_C'])
    ep_api.exchange.set_actuator_value(state, allHandles['actuator']['Boiler_SET_C'], to_set['Boiler_SET_C'])
    ep_api.exchange.set_actuator_value(state, allHandles['actuator']['OAT_C'], to_set['OAT_C'])
    ep_api.exchange.set_actuator_value(state, allHandles['actuator']['RH_percent'], to_set['RH_percent'])
    for i in range(len(allHandles['actuator']['Damper_Position'])):
        ep_api.exchange.set_actuator_value(state, allHandles['actuator']['Damper_Position'][i], to_set['Damper_Position'][i])
def api_to_csv(state):
    orig = ep_api.exchange.list_available_api_data_csv(state)
    newFileByteArray = bytearray(orig)
    api_path = os.path.join(os.path.dirname(__file__), 'api_data.csv')
    newFile = open(api_path, "wb")
    newFile.write(newFileByteArray)
    newFile.close()
def timeStepHandler(state):
    global get_handle_bool
    if not get_handle_bool:
        get_building_handles(state)
        get_handle_bool = True
        api_to_csv(state)
    warm_up = ep_api.exchange.warmup_flag(state)
    if not warm_up:
        sensor_values = get_sensor_value(state)
        print(sensor_values)
        set_actuators(state, sensor_values)
def init():
    sys.path.insert(0, '/usr/local/EnergyPlus-22-1-0/')
    sys.path.insert(0, 'C:/EnergyPlusV22-1-0')
    from pyenergyplus.api import EnergyPlusAPI
    global ep_api, get_handle_bool
    get_handle_bool = False
    ep_api = EnergyPlusAPI()
    state = ep_api.state_manager.new_state()
    ep_api.runtime.callback_after_predictor_before_hvac_managers(state, timeStepHandler)
    ep_api.exchange.request_variable(state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")
    ep_api.exchange.request_variable(state, "Site Outdoor Air Humidity Ratio", "ENVIRONMENT")
    ep_api.exchange.request_variable(state, "Site Mains Water Temperature", "ENVIRONMENT")
    return state

def main():
    state = init()
    idfFilePath = os.path.join(os.path.dirname(__file__), 'resources','idf',
                               'RefBldgLargeOfficeNew2004_v1.4_7.2_5A_USA_IL_CHICAGO-OHARE_V2210.idf')
    weather_file_path = os.path.join(os.path.dirname(__file__), 'resources','epw',
                                     'USA_IL_Chicago-OHare.Intl.AP.725300_TMY3_No_Precipitable_Water.epw')
    output_path = './ep_trivial'
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    ep_api.runtime.run_energyplus(state, sys_args)

if __name__ == '__main__':
    main()
