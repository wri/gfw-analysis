

def dict(admin_level,adm0,adm1,adm2,column_name):
    admin_level = str(admin_level)
    admin_dict = {'national': {'level': adm0, 'column_name': 'adm0_id', 'area_type': 'nat', 'column_calc':  """!ISO!+"_"+ str("""""""""""+"!" + column_name + "!"+""""""""")"""} ,
                  'subnational': {'level': adm1, 'column_name': 'adm1_id','area_type': 'subnat', 'column_calc': """!ISO!+str( !ID_1!)+"_"+ str("""""""""""+"!" + column_name + "!"+""""""""")""" },
                  'district': {'level': adm2, 'column_name': 'adm2_id', 'area_type': 'dist', 'column_calc': """!ISO!+str( !ID_1!)+"d"+str( !ID_2!)+"_"+ str("""""""""""+"!" + column_name + "!"+""""""""")"""}}

    column_name_d = admin_dict[admin_level]['column_name']
    column_calc_d = admin_dict[admin_level]['column_calc']
    area_type_d = admin_dict[admin_level]['area_type']
    admin_level_d = admin_dict[admin_level]['level']

    return column_name_d, column_calc_d, area_type_d, admin_level_d



    # admin_level_dict = {'national':adm0,'subnational':adm1,'district':adm2}
    # column_name_dict = {'national':'adm0_id','subnational':'adm1_id','district':'adm2_id'}
    # area_type_dict = {'national':'nat','subnational':'subnat','district':'dist'}
    # column_calc_dict = {'national': """!ISO!+"_"+ str("""""""""""+"!" + column_name + "!"+""""""""")""",
    #                     'subnational': """!ISO!+str( !ID_1!)+"_"+ str("""""""""""+"!" + column_name + "!"+""""""""")""",
    #                     'district': """!ISO!+str( !ID_1!)+"d"+str( !ID_2!)+"_"+ str("""""""""""+"!" + column_name + "!"+""""""""")"""}
    #
    # return column_name_dict[admin_level],column_calc_dict[admin_level], area_type_dict[admin_level], admin_level_dict[admin_level]