__author__ = 'sgibbes'
def dict(admin_level,adm0,adm1,adm2):
    admin_level_dict = {'national':adm0,'subnational':adm1,'district':adm2}
    column_name_dict = {'national':'adm0_id','subnational':'adm1_id','district':'adm2_id'}
    area_type_dict = {'national':'nat','subnational':'subnat','district':'dist'}
    column_calc_dict = {'national':"""!ISO!+"_"+ str(!FID!)""",'subnational':"""!ISO!+str( !ID_1!)+"_"+ str(!FID!)""",'district':"""!ISO!+"d"+str( !ID_2!)+"_"+ str(!FID!)"""}
    return column_name_dict[admin_level],column_calc_dict[admin_level], area_type_dict[admin_level], admin_level_dict[admin_level]