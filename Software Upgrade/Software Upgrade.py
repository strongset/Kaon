# -*- coding: utf-8 -*-
# Test name = Software Upgrade
# Test description = Set environment, perform software upgrade and check STB state after sw upgrade

from datetime import datetime
from time import gmtime, strftime
import time
import os.path
import sys
import device
#import subprocess
import TEST_CREATION_API
import shutil
##shutil.copyfile('\\\\bbtfs\\RT-Executor\\API\\NOS_API.py', 'NOS_API.py')

try:    
    if ((os.path.exists(os.path.join(os.path.dirname(sys.executable), "Lib\NOS_API.py")) == False) or (str(os.path.getmtime('\\\\rt-rk01\\RT-Executor\\API\\NOS_API.py')) != str(os.path.getmtime(os.path.join(os.path.dirname(sys.executable), "Lib\NOS_API.py"))))):
        shutil.copy2('\\\\rt-rk01\\RT-Executor\\API\\NOS_API.py', os.path.join(os.path.dirname(sys.executable), "Lib\NOS_API.py"))
except:
    pass

import NOS_API    

try:
    # Get model
    model_type = NOS_API.get_model()

    # Check if folder with thresholds exists, if not create it
    if(os.path.exists(os.path.join(os.path.dirname(sys.executable), "Thresholds")) == False):
        os.makedirs(os.path.join(os.path.dirname(sys.executable), "Thresholds"))

    # Copy file with threshold if does not exists or if it is updated
    if ((os.path.exists(os.path.join(os.path.dirname(sys.executable), "Thresholds\\" + model_type + ".txt")) == False) or (str(os.path.getmtime(NOS_API.THRESHOLDS_PATH + model_type + ".txt")) != str(os.path.getmtime(os.path.join(os.path.dirname(sys.executable), "Thresholds\\" + model_type + ".txt"))))):
        shutil.copy2(NOS_API.THRESHOLDS_PATH + model_type + ".txt", os.path.join(os.path.dirname(sys.executable), "Thresholds\\" + model_type + ".txt"))
except Exception as error_message:
    pass 
 
# Time in seconds which define when dialog will be closed
DIALOG_TIMEOUT = 10

## Number of alphanumeric characters in SN
SN_LENGTH = 16  

## Number of alphanumeric characters in Cas_Id
CASID_LENGTH = 12

## Number of alphanumeric characters in MAC
MAC_LENGTH = 12   

WAIT_FOR_UPDATE = 10

## Time needed to STB power on (in seconds)
WAIT_TO_POWER_STB = 20

## Time to press V+/V- simultaneous in seconds
TIMEOUT_CAUSE_SW_UPGRADE = 4

## Time to switch from HDMI to SCART in seconds
WAIT_TO_SWITCH_SCART = 6

def runTest():

    try:        
        NOS_API.read_thresholds()
        ## Set test result default to FAIL
        test_result = "FAIL"
        HDMI_Threshold = TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD
        boot_sequence = 0
        error_codes = ""
        error_messages = ""
        SN_LABEL = False
        CASID_LABEL = False
        MAC_LABEL = False
        Hardware_Result = False
        SW_Upgrade = False
        NOS_API.SET_720 = False
       
        ## Reset all global variables 
        NOS_API.reset_test_cases_results_info()
              
        try:
           
            ## Perform scanning with barcode scanner   
            all_scanned_barcodes = NOS_API.get_all_scanned_barcodes()     
            NOS_API.test_cases_results_info.s_n_using_barcode = all_scanned_barcodes[1]
            NOS_API.test_cases_results_info.cas_id_using_barcode = all_scanned_barcodes[2]
            NOS_API.test_cases_results_info.mac_using_barcode = all_scanned_barcodes[3]
            NOS_API.test_cases_results_info.nos_sap_number = all_scanned_barcodes[0]
        except Exception as error:   
            TEST_CREATION_API.write_log_to_file(error)
            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.scan_error_code \
                                        + "; Error message: " + NOS_API.test_cases_results_info.scan_error_message)
            NOS_API.set_error_message("Leitura de Etiquetas")
            error_codes = NOS_API.test_cases_results_info.scan_error_code
            error_messages = NOS_API.test_cases_results_info.scan_error_message
            
            NOS_API.add_test_case_result_to_file_report(
                    test_result,
                    "- - - - - - - - - - - - - - - - - - - -",
                    "- - - - - - - - - - - - - - - - - - - -",
                    error_codes,
                    error_messages)
    
            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            report_file = NOS_API.create_test_case_log_file(
                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                NOS_API.test_cases_results_info.nos_sap_number,
                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                NOS_API.test_cases_results_info.mac_using_barcode,
                                end_time)
            NOS_API.upload_file_report(report_file)      
            NOS_API.test_cases_results_info.isTestOK = False
            
            ## Update test result
            TEST_CREATION_API.update_test_result(test_result)
            
            NOS_API.send_report_over_mqtt_test_plan(
                    test_result,
                    end_time,
                    error_codes,
                    report_file)
    
            return

        test_number = NOS_API.get_test_number(NOS_API.test_cases_results_info.s_n_using_barcode)
        device.updateUITestSlotInfo("Teste N\xb0: " + str(int(test_number)+1))
        
        if ((len(NOS_API.test_cases_results_info.s_n_using_barcode) == SN_LENGTH) and (NOS_API.test_cases_results_info.s_n_using_barcode.isalnum() or NOS_API.test_cases_results_info.s_n_using_barcode.isdigit())):
            SN_LABEL = True
             
        if ((len(NOS_API.test_cases_results_info.cas_id_using_barcode) == CASID_LENGTH) and (NOS_API.test_cases_results_info.cas_id_using_barcode.isalnum() or NOS_API.test_cases_results_info.cas_id_using_barcode.isdigit())):
            CASID_LABEL = True
    
        if ((len(NOS_API.test_cases_results_info.mac_using_barcode) == MAC_LENGTH) and (NOS_API.test_cases_results_info.mac_using_barcode.isalnum() or NOS_API.test_cases_results_info.mac_using_barcode.isdigit()) and NOS_API.test_cases_results_info.mac_using_barcode != NOS_API.test_cases_results_info.cas_id_using_barcode):
            MAC_LABEL = True
            
        
        if (SN_LABEL and CASID_LABEL and MAC_LABEL):               
            if (NOS_API.display_new_dialog("Conectores?", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):                 
                if (NOS_API.display_new_dialog("Painel Traseiro?", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):   
                    Hardware_Result = True                                  
                else:
                    TEST_CREATION_API.write_log_to_file("Back Panel NOK")
                    NOS_API.set_error_message("Danos Externos")
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.back_panel_nok_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.back_panel_nok_error_message) 
                    error_codes = NOS_API.test_cases_results_info.back_panel_nok_error_code
                    error_messages = NOS_API.test_cases_results_info.back_panel_nok_error_message 
            else:       
                TEST_CREATION_API.write_log_to_file("Conectores NOK")
                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.conector_nok_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.conector_nok_error_message)
                NOS_API.set_error_message("Danos Externos")
                error_codes = NOS_API.test_cases_results_info.conector_nok_error_code
                error_messages = NOS_API.test_cases_results_info.conector_nok_error_message
        else:
            TEST_CREATION_API.write_log_to_file("Labels Scaning")
            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.scan_error_code \
                                        + "; Error message: " + NOS_API.test_cases_results_info.scan_error_message)
            NOS_API.set_error_message("Leitura de Etiquetas")
            error_codes = NOS_API.test_cases_results_info.scan_error_code
            error_messages = NOS_API.test_cases_results_info.scan_error_message
   
        if(Hardware_Result):
            NOS_API.initialize_grabber()
        
            ## Start grabber device with video on default video source
            NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
            
            NOS_API.Send_Serial_Key("a", "feito")
            
            ## Power off STB with energenie
            if (NOS_API.configure_power_switch()):
                if not(NOS_API.power_off()): 
                    TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                    ## Update test result
                    TEST_CREATION_API.update_test_result(test_result)
                    NOS_API.set_error_message("Inspection")
                
                    NOS_API.add_test_case_result_to_file_report(
                                    test_result,
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    error_codes,
                                    error_messages)
                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                    report_file = ""
                    if (test_result != "PASS"):
                        report_file = NOS_API.create_test_case_log_file(
                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                        NOS_API.test_cases_results_info.nos_sap_number,
                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                        "",
                                        end_time)
                        NOS_API.upload_file_report(report_file)
                        NOS_API.test_cases_results_info.isTestOK = False
                    
                        NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)                
            
                    ## Return DUT to initial state and de-initialize grabber device
                    NOS_API.deinitialize()
    
                    return
                time.sleep(1)
            else:
                TEST_CREATION_API.write_log_to_file("Incorrect test place name")
            
                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_switch_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.power_switch_error_message)
                NOS_API.set_error_message("Inspection")

                ## Return DUT to initial state and de-initialize grabber device
                NOS_API.deinitialize()
            
                NOS_API.add_test_case_result_to_file_report(
                                test_result,
                                "- - - - - - - - - - - - - - - - - - - -",
                                "- - - - - - - - - - - - - - - - - - - -",
                                error_codes,
                                error_messages)
                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                report_file = ""
                if (test_result != "PASS"):
                    report_file = NOS_API.create_test_case_log_file(
                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                    NOS_API.test_cases_results_info.nos_sap_number,
                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                    "",
                                    end_time)
                    NOS_API.upload_file_report(report_file)
                    NOS_API.test_cases_results_info.isTestOK = False
            
            
                ## Update test result
                TEST_CREATION_API.update_test_result(test_result)

                NOS_API.upload_file_report(report_file)

                NOS_API.send_report_over_mqtt_test_plan(
                    test_result,
                    end_time,
                    error_codes,
                    report_file)
    
                return        
            
             
            while(boot_sequence < 3):
                if not(NOS_API.power_off()):
                    TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                    ## Update test result
                    TEST_CREATION_API.update_test_result(test_result)
                    NOS_API.set_error_message("Inspection")
                
                    NOS_API.add_test_case_result_to_file_report(
                                    test_result,
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    error_codes,
                                    error_messages)
                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')    
                    report_file = ""
                    if (test_result != "PASS"):
                        report_file = NOS_API.create_test_case_log_file(
                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                        NOS_API.test_cases_results_info.nos_sap_number,
                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                        "",
                                        end_time)
                        NOS_API.upload_file_report(report_file)
                        NOS_API.test_cases_results_info.isTestOK = False

            
                    ## Return DUT to initial state and de-initialize grabber device
                    NOS_API.deinitialize()
                
                    NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)

                    return
        
                NOS_API.display_custom_dialog("Pressione no bot\xe3o CH+(^) da STB", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                
                if not(NOS_API.power_on()):
                    TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                    ## Update test result
                    TEST_CREATION_API.update_test_result(test_result)
                    NOS_API.set_error_message("Inspection")
                
                    NOS_API.add_test_case_result_to_file_report(
                                    test_result,
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    error_codes,
                                    error_messages)
                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')    
                    report_file = ""
                    if (test_result != "PASS"):
                        report_file = NOS_API.create_test_case_log_file(
                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                        NOS_API.test_cases_results_info.nos_sap_number,
                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                        "",
                                        end_time)
                        NOS_API.upload_file_report(report_file)
                        NOS_API.test_cases_results_info.isTestOK = False
    
            
                    ## Return DUT to initial state and de-initialize grabber device
                    NOS_API.deinitialize()
                
                    NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)
    
                    return
                                
                
                start_time = int(time.time())
                result = NOS_API.display_custom_dialog("", 1, ["Repetir"], WAIT_FOR_UPDATE)
                timeout = int(time.time()) - start_time
                if (result == "Repetir"):                    
                    if (timeout >= WAIT_FOR_UPDATE):                 
                    
                        if(boot_sequence == 0):
                            if not(NOS_API.display_custom_dialog("A STB est\xe1 ligada? Insira o SmartCard!", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                                TEST_CREATION_API.write_log_to_file("No Power")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.no_power_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.no_power_error_message) 
                                NOS_API.set_error_message("Não Liga") 
                                error_codes =  NOS_API.test_cases_results_info.no_power_error_code
                                error_messages = NOS_API.test_cases_results_info.no_power_error_message
                                NOS_API.deinitialize()
                                
                                NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                            
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                                NOS_API.upload_file_report(report_file)
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                            
                            
                                return
                        if(NOS_API.wait_for_signal_present(30)):           
                            Update_Screen = NOS_API.wait_for_multiple_pictures(["SW_Update_720_REF"], 30, ["[Update_720]"], [HDMI_Threshold])
                            if(Update_Screen == 0):
                                Update_image = NOS_API.wait_for_multiple_pictures(["SW_Update_Success_720_REF"], 110, ["[Update_Success_720]"], [HDMI_Threshold])
                                if(Update_image == 0):
                                    NOS_API.test_cases_results_info.DidUpgrade = 1
                                    SW_Upgrade = True
                                    boot_sequence = 4
                                    continue
                                elif(boot_sequence == 2):
                                    TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                    NOS_API.set_error_message("Não Actualiza") 
                                    error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                                    NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                    
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                                                            
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                            
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    return
                
                                boot_sequence = boot_sequence + 1
                                continue
                            if(Update_Screen == -1):
                                if(boot_sequence == 2):
                                    TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                    NOS_API.set_error_message("Não Actualiza") 
                                    error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                                    NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                    
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                                                            
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                            
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    return
                
                                boot_sequence = boot_sequence + 1
                                continue
                            if(Update_Screen == -2):
                                NOS_API.display_custom_dialog("Confirme o cabo HDMI", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                                time.sleep(2)
                                
                                Update_Screen = NOS_API.wait_for_multiple_pictures(["SW_Update_720_REF","SW_Update_Success_720_REF"], 90, ["[Update_720]","[Update_Success_720]"], [HDMI_Threshold,HDMI_Threshold])
                                if(Update_Screen == 0):
                                    Update_image = NOS_API.wait_for_multiple_pictures(["SW_Update_Success_720_REF"], 110, ["[Update_Success_720]"], [HDMI_Threshold])
                                    if(Update_image == 0):
                                        NOS_API.test_cases_results_info.DidUpgrade = 1
                                        SW_Upgrade = True
                                        boot_sequence = 4
                                        continue
                                    elif(boot_sequence == 2):
                                        TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                        NOS_API.set_error_message("Não Actualiza") 
                                        error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                                        NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                    
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                    
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                                                                
                                        NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                                
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        return
                
                                    boot_sequence = boot_sequence + 1
                                    
                                    if(Update_image == -1):
                                        if(boot_sequence == 2):
                                            TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                            NOS_API.set_error_message("Não Actualiza") 
                                            error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                                        boot_sequence = boot_sequence + 1
                                        continue
                                
        
                                if(Update_Screen == 1):
                                    NOS_API.test_cases_results_info.DidUpgrade = 1
                                    SW_Upgrade = True
                                    boot_sequence = 4
                                    continue
                                if(Update_Screen == -1):
                                    if(boot_sequence == 2):
                                        TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                        NOS_API.set_error_message("Não Actualiza") 
                                        error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                                    boot_sequence = boot_sequence + 1
                                    continue
                            
                                if(Update_Screen == -2):
                                    TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                    NOS_API.set_error_message("Video HDMI")
                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                    
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                                                            
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                            
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    return
                    
                        else:
                        
                            if(boot_sequence == 0):
                                NOS_API.display_custom_dialog("Confirme o cabo HDMI", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                                time.sleep(2)
                            if(NOS_API.wait_for_signal_present(5)):
                                Update_Screen = NOS_API.wait_for_multiple_pictures(["SW_Update_720_REF"], 30, ["[Update_720]"], [HDMI_Threshold])
                                if(Update_Screen == 0):
                                    Update_image = NOS_API.wait_for_multiple_pictures(["SW_Update_Success_720_REF"], 110, ["[Update_Success_720]"], [HDMI_Threshold])
                                    if(Update_image == 0):
                                        NOS_API.test_cases_results_info.DidUpgrade = 1
                                        SW_Upgrade = True
                                        boot_sequence = 4
                                        continue
                                if(Update_Screen == -1):
                                    if(boot_sequence == 2):
                                        TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                        NOS_API.set_error_message("Não Actualiza") 
                                        error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                                    boot_sequence = boot_sequence + 1
                                    continue
                                if(Update_Screen == -2):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return
                                    
                            
                            else:
                                
                                boot_sequence = boot_sequence + 1
                                continue

                boot_sequence = boot_sequence + 1
  
            if(boot_sequence == 3):
                TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                NOS_API.set_error_message("Video HDMI")
                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                
                NOS_API.add_test_case_result_to_file_report(
                            test_result,
                            "- - - - - - - - - - - - - - - - - - - -",
                            "- - - - - - - - - - - - - - - - - - - -",
                            error_codes,
                            error_messages)

                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                report_file = NOS_API.create_test_case_log_file(
                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                NOS_API.test_cases_results_info.nos_sap_number,
                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                NOS_API.test_cases_results_info.mac_using_barcode,
                                end_time)
            
                NOS_API.upload_file_report(report_file)
                NOS_API.test_cases_results_info.isTestOK = False
                                        
                NOS_API.send_report_over_mqtt_test_plan(
                        test_result,
                        end_time,
                        error_codes,
                        report_file)
                        
                ## Update test result
                TEST_CREATION_API.update_test_result(test_result)
                
                ## Return DUT to initial state and de-initialize grabber device
                NOS_API.deinitialize()
                
                return
    
            if(SW_Upgrade):
                boot_image = NOS_API.wait_for_multiple_pictures(["Install_ref","HDMI_Video_1080_ref","HDMI_Video_720_ref","No_signal_1080p_ref","No_signal_720p_ref"], 90, ["[Install_menu]","[HALF_SCREEN_1080]","[HALF_SCREEN_720]","[NO_SIGNAL_1080]","[NO_SIGNAL_720]"], [HDMI_Threshold,HDMI_Threshold,HDMI_Threshold,HDMI_Threshold,HDMI_Threshold])
                TEST_CREATION_API.write_log_to_file(boot_image)
                if(boot_image == 0):
                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                    signal_image = NOS_API.wait_for_multiple_pictures(["Install_ref","Set_signal_ref"], 10, ["[Install_menu]","[NO_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                    if(signal_image == 0):
                        TEST_CREATION_API.send_ir_rc_command("[OK]")
                        signal_image = NOS_API.wait_for_multiple_pictures(["Install_ref","Set_signal_ref"], 10, ["[Install_menu]","[NO_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                        if(signal_image == 0):
                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                        + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                            NOS_API.set_error_message("IR")
                            error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                            error_messages = NOS_API.test_cases_results_info.ir_nok_error_message 
                            test_result = "FAIL"
                            NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = ""
                            if (test_result != "PASS"):
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False
            
            
                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
            
                            return
                
                        elif(signal_image == 1):
                            NOS_API.display_custom_dialog("Confirme o cabo RF", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                            time.sleep(1)
                            signal_image = NOS_API.wait_for_multiple_pictures(["Set_signal_ref"], 10, ["[NO_INSTALL]"], [HDMI_Threshold])
                            if(signal_image == 0):
                                TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold")                
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                                NOS_API.set_error_message("Sem Sinal")
                                error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                                error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                
                                return
                   
                    elif(signal_image == 1):
                        NOS_API.display_custom_dialog("Confirme o cabo RF", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                        time.sleep(1)
                        signal_image = NOS_API.wait_for_multiple_pictures(["Set_signal_ref"], 10, ["[NO_INSTALL]"], [HDMI_Threshold])
                        if(signal_image == 0):
                            TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold")                
                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                            NOS_API.set_error_message("Sem Sinal")
                            error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                            error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                            NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = ""
                            if (test_result != "PASS"):
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False
            
            
                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
            
                            return
           
                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                    Install_image = NOS_API.wait_for_multiple_pictures(["Install_Success_ref"], 5, ["[SEARCH]"], [HDMI_Threshold])
                    if(Install_image != 0):
                        TEST_CREATION_API.send_ir_rc_command("[OK]")
                    Install_Success_image = NOS_API.wait_for_multiple_pictures(["Install_Success_ref","Install_Success_ref1"], 30, ["[SUCCESS_INSTALL]","[SUCCESS_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                    
                    if(Install_Success_image == 0):
                        TEST_CREATION_API.send_ir_rc_command("[OK]")
                        TEST_CREATION_API.send_ir_rc_command("[BACK]")
                        TEST_CREATION_API.send_ir_rc_command("[CH_3]")
                    else:
                        TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold") 
                        TEST_CREATION_API.write_log_to_file("Falhou a meio da atualização")                                 
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                        NOS_API.set_error_message("Sem Sinal")
                        error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                        error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False
        
        
                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)
        
                        return

                    signal_image = NOS_API.wait_for_multiple_pictures(["HDMI_Video_1080_ref"], 10, ["[HALF_SCREEN_1080]"], [HDMI_Threshold])
                    if(signal_image == 0):
                        test_result = "PASS"
                    elif(signal_image == -1):
                        TEST_CREATION_API.write_log_to_file("Image is not reproduced correctly on HDMI.")
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message)
                        error_codes = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code
                        error_messages = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message
                        NOS_API.set_error_message("Video HDMI")
                    
                    elif(signal_image == -2):
                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                        NOS_API.set_error_message("Reboot")
                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                        test_result = "FAIL"
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False
        
        
                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)
        
                        return
                
                elif(boot_image >= 1 and boot_image <= 2): 
                    if(boot_image == 2):
                        NOS_API.SET_720 = True
                    test_result = "PASS"
                
                elif(boot_image == -1 or (boot_image >= 3 and boot_image <= 4)):
                    if(boot_image == -1):
                        TEST_CREATION_API.send_ir_rc_command("[CH_3]")
                        Status_Image = NOS_API.wait_for_multiple_pictures(["HDMI_Video_1080_ref","HDMI_Video_720_ref"], 5, ["[HALF_SCREEN_1080]","[HALF_SCREEN_720]"], [HDMI_Threshold,HDMI_Threshold])
                        if(Status_Image >= 0 and Status_Image <= 1): 
                            if(Status_Image == 1):
                                NOS_API.SET_720 = True
                            test_result = "PASS"
                                               
                            NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = ""
                            if (test_result != "PASS"):
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                            
                            
                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)

                            if(Hardware_Result):
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                           
                                                
                                                
                            return                
                    
                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                    TEST_CREATION_API.send_ir_rc_command("[FACTORY_RESET]")
                    if(NOS_API.wait_for_no_signal_present(15)):
                        boot_image = NOS_API.wait_for_multiple_pictures(["Install_ref"], 90, ["[Install_menu]"], [HDMI_Threshold])
                        TEST_CREATION_API.write_log_to_file(boot_image)
                        if(boot_image == 0):
                            TEST_CREATION_API.send_ir_rc_command("[OK]")
                            signal_image = NOS_API.wait_for_multiple_pictures(["Install_ref","Set_signal_ref"], 10, ["[Install_menu]","[NO_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                            if(signal_image == 0):
                                TEST_CREATION_API.send_ir_rc_command("[OK]")
                                signal_image = NOS_API.wait_for_multiple_pictures(["Install_ref","Set_signal_ref"], 10, ["[Install_menu]","[NO_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                                if(signal_image == 0):
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                    NOS_API.set_error_message("IR")
                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message 
                                    test_result = "FAIL"
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return
                        
                                elif(signal_image == 1):
                                    NOS_API.display_custom_dialog("Confirme o cabo RF", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                                    time.sleep(1)
                                    signal_image = NOS_API.wait_for_multiple_pictures(["Set_signal_ref"], 10, ["[NO_INSTALL]"], [HDMI_Threshold])
                                    if(signal_image == 0):
                                        TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold")                
                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                                        NOS_API.set_error_message("Sem Sinal")
                                        error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                                        error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                        
                                        return
                                        
                              
                            elif(signal_image == 1):
                                NOS_API.display_custom_dialog("Confirme o cabo RF", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                                time.sleep(1)
                                signal_image = NOS_API.wait_for_multiple_pictures(["Set_signal_ref"], 10, ["[NO_INSTALL]"], [HDMI_Threshold])
                                if(signal_image == 0):
                                    TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold")                
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                                    NOS_API.set_error_message("Sem Sinal")
                                    error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                                    error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return
                           
                            elif(signal_image == -2):   
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                
                                return
                            
                                                        
                            
                            TEST_CREATION_API.send_ir_rc_command("[OK]")
                            Install_image = NOS_API.wait_for_multiple_pictures(["Install_Success_ref"], 5, ["[SEARCH]"], [HDMI_Threshold])
                            if(Install_image != 0):
                                TEST_CREATION_API.send_ir_rc_command("[OK]")
                            Install_Success_image = NOS_API.wait_for_multiple_pictures(["Install_Success_ref","Install_Success_ref1"], 30, ["[SUCCESS_INSTALL]","[SUCCESS_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                            
                            if(Install_Success_image == 0):
                                TEST_CREATION_API.send_ir_rc_command("[OK]")
                                TEST_CREATION_API.send_ir_rc_command("[BACK]")
                                TEST_CREATION_API.send_ir_rc_command("[CH_3]")
                            else:
                                TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold") 
                                TEST_CREATION_API.write_log_to_file("Falhou a meio da atualização")                                 
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                                NOS_API.set_error_message("Sem Sinal")
                                error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                                error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                
                                return
                       
                 
                            signal_image = NOS_API.wait_for_multiple_pictures(["HDMI_Video_1080_ref"], 15, ["[HALF_SCREEN_1080]"], [HDMI_Threshold])
                            if(signal_image == 0):
                                test_result = "PASS"
                            elif(signal_image == -1):
                                TEST_CREATION_API.write_log_to_file("Image is not reproduced correctly on HDMI.")
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message)
                                error_codes = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code
                                error_messages = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message
                                NOS_API.set_error_message("Video HDMI")
                            
                            elif(signal_image == -2):
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                
                                return
            
                        
                        else:
                            TEST_CREATION_API.write_log_to_file("Image is not reproduced correctly on HDMI.")
                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message)
                            error_codes = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code
                            error_messages = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message
                            NOS_API.set_error_message("Video HDMI")
                                
                                
                    else:
                        TEST_CREATION_API.send_ir_rc_command("[CH_3]")
                        time.sleep(1)
                        TEST_CREATION_API.send_ir_rc_command("[BACK]")
                        TEST_CREATION_API.send_ir_rc_command("[BACK]")
                        TEST_CREATION_API.send_ir_rc_command("[FACTORY_RESET]")
                        if(NOS_API.wait_for_no_signal_present(15)):
                            boot_image = NOS_API.wait_for_multiple_pictures(["Install_ref"], 90, ["[Install_menu]"], [HDMI_Threshold])
                            TEST_CREATION_API.write_log_to_file(boot_image)
                            if(boot_image == 0):
                                TEST_CREATION_API.send_ir_rc_command("[OK]")
                                
                                signal_image = NOS_API.wait_for_multiple_pictures(["Install_ref","Set_signal_ref"], 10, ["[Install_menu]","[NO_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                                if(signal_image == 0):
                                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                                    signal_image = NOS_API.wait_for_multiple_pictures(["Install_ref","Set_signal_ref"], 10, ["[Install_menu]","[NO_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                                    if(signal_image == 0):
                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                        NOS_API.set_error_message("IR")
                                        error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.ir_nok_error_message 
                                        test_result = "FAIL"
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                        
                                        return
                            
                                    elif(signal_image == 1):
                                        NOS_API.display_custom_dialog("Confirme o cabo RF", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                                        time.sleep(1)
                                        signal_image = NOS_API.wait_for_multiple_pictures(["Set_signal_ref"], 10, ["[NO_INSTALL]"], [HDMI_Threshold])
                                        if(signal_image == 0):
                                            TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold")                
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                                            NOS_API.set_error_message("Sem Sinal")
                                            error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                                            error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                            
                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                            
                                            return
                                            
                                  
                                elif(signal_image == 1):
                                    NOS_API.display_custom_dialog("Confirme o cabo RF", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                                    time.sleep(1)
                                    signal_image = NOS_API.wait_for_multiple_pictures(["Set_signal_ref"], 10, ["[NO_INSTALL]"], [HDMI_Threshold])
                                    if(signal_image == 0):
                                        TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold")                
                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                                        NOS_API.set_error_message("Sem Sinal")
                                        error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                                        error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                        
                                        return
                                        
                                

                                elif(signal_image == -2):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return
                                
                                
                                TEST_CREATION_API.send_ir_rc_command("[OK]")
                                Install_image = NOS_API.wait_for_multiple_pictures(["Install_Success_ref"], 5, ["[SEARCH]"], [HDMI_Threshold])
                                if(Install_image != 0):
                                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                                Install_Success_image = NOS_API.wait_for_multiple_pictures(["Install_Success_ref","Install_Success_ref1"], 30, ["[SUCCESS_INSTALL]","[SUCCESS_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                                
                                if(Install_Success_image == 0):
                                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                                    TEST_CREATION_API.send_ir_rc_command("[CH_3]")
                                else:
                                    TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold") 
                                    TEST_CREATION_API.write_log_to_file("Falhou a meio da atualização")                                 
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                                    NOS_API.set_error_message("Sem Sinal")
                                    error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                                    error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return
                           
                     
                                signal_image = NOS_API.wait_for_multiple_pictures(["HDMI_Video_1080_ref"], 15, ["[HALF_SCREEN_1080]"], [HDMI_Threshold])
                                if(signal_image == 0):
                                    test_result = "PASS"
                                elif(signal_image == -1):
                                    TEST_CREATION_API.write_log_to_file("Image is not reproduced correctly on HDMI.")
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message)
                                    error_codes = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code
                                    error_messages = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message
                                    NOS_API.set_error_message("Video HDMI")
                                
                                elif(signal_image == -2):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return
    
                            else:
                                TEST_CREATION_API.write_log_to_file("Image is not reproduced correctly on HDMI.")
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message)
                                error_codes = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code
                                error_messages = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message
                                NOS_API.set_error_message("Video HDMI")
                                    
                                    
                        else:
                            NOS_API.set_error_message("Navegação")                    
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                            error_codes = NOS_API.test_cases_results_info.navigation_error_code
                            error_messages = NOS_API.test_cases_results_info.navigation_error_message                    
                            
                            NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                            
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            report_file = ""    
                            
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
        
                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
        
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            return
                            
                        
                elif(boot_image == -2): 
                    counter = 0
                    liga = True
                    while(counter < 2):
                        if(liga):
                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                            if not(NOS_API.wait_for_signal_present(5)):
                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                            liga = False
                        TEST_CREATION_API.send_ir_rc_command("[BACK]")
                        TEST_CREATION_API.send_ir_rc_command("[CH_3]")
                        signal_image = NOS_API.wait_for_multiple_pictures(["HDMI_Video_1080_ref","HDMI_Video_720_ref","No_signal_1080p_ref","No_signal_720p_ref","Install_ref"], 10, ["[HALF_SCREEN_1080]","[HALF_SCREEN_720]","[NO_SIGNAL_1080]","[NO_SIGNAL_720]","[Install_menu]"], [HDMI_Threshold,HDMI_Threshold,HDMI_Threshold,HDMI_Threshold,HDMI_Threshold])
                        if(signal_image >= 0 and signal_image <= 1):
                            if(signal_image == 1):
                                NOS_API.SET_720 = True
                            test_result = "PASS"
                            counter = 3
                        elif(signal_image >= 2 and signal_image <= 3):
                            if(counter == 0):
                                NOS_API.display_custom_dialog("Confirme o cabo RF", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                                time.sleep(2)
                            TEST_CREATION_API.send_ir_rc_command("[BACK]")
                            TEST_CREATION_API.send_ir_rc_command("[BACK]")
                            TEST_CREATION_API.send_ir_rc_command("[FACTORY_RESET]")
                            if(NOS_API.wait_for_no_signal_present(15)):
                                boot_image = NOS_API.wait_for_multiple_pictures(["Install_ref"], 90, ["[Install_menu]"], [HDMI_Threshold])
                                TEST_CREATION_API.write_log_to_file(boot_image)
                                if(boot_image == 0):
                                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                                    signal_image = NOS_API.wait_for_multiple_pictures(["Install_ref","Set_signal_ref"], 10, ["[Install_menu]","[NO_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                                    if(signal_image == 0):
                                        TEST_CREATION_API.send_ir_rc_command("[OK]")
                                        signal_image = NOS_API.wait_for_multiple_pictures(["Install_ref","Set_signal_ref"], 10, ["[Install_menu]","[NO_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                                        if(signal_image == 0):
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                            NOS_API.set_error_message("IR")
                                            error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.ir_nok_error_message 
                                            test_result = "FAIL"
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                            
                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                            
                                            return
                                
                                        elif(signal_image == 1):
                                            NOS_API.display_custom_dialog("Confirme o cabo RF", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                                            time.sleep(1)
                                            signal_image = NOS_API.wait_for_multiple_pictures(["Set_signal_ref"], 10, ["[NO_INSTALL]"], [HDMI_Threshold])
                                            if(signal_image == 0):
                                                TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold")                
                                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                                                NOS_API.set_error_message("Sem Sinal")
                                                error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                                                error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                
                                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                
                                                return
                                                
                                      
                                    elif(signal_image == 1):
                                        NOS_API.display_custom_dialog("Confirme o cabo RF", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                                        time.sleep(1)
                                        signal_image = NOS_API.wait_for_multiple_pictures(["Set_signal_ref"], 10, ["[NO_INSTALL]"], [HDMI_Threshold])
                                        if(signal_image == 0):
                                            TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold")                
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                                            NOS_API.set_error_message("Sem Sinal")
                                            error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                                            error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                            
                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                            
                                            return
                                           
                                 
                            else:
                                TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold")                
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                                NOS_API.set_error_message("Sem Sinal")
                                error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                                error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                                break
                                
                                
                            counter += 1
                        elif(signal_image == 4):
                            TEST_CREATION_API.send_ir_rc_command("[OK]")
                            signal_image = NOS_API.wait_for_multiple_pictures(["Install_ref","Set_signal_ref"], 10, ["[Install_menu]","[NO_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                            if(signal_image == 0):
                                TEST_CREATION_API.send_ir_rc_command("[OK]")
                                signal_image = NOS_API.wait_for_multiple_pictures(["Install_ref","Set_signal_ref"], 10, ["[Install_menu]","[NO_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                                if(signal_image == 0):
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                    NOS_API.set_error_message("IR")
                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message 
                                    test_result = "FAIL"
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return
                        
                                elif(signal_image == 1):
                                    NOS_API.display_custom_dialog("Confirme o cabo RF", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                                    time.sleep(1)
                                    signal_image = NOS_API.wait_for_multiple_pictures(["Set_signal_ref"], 10, ["[NO_INSTALL]"], [HDMI_Threshold])
                                    if(signal_image == 0):
                                        TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold")                
                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                                        NOS_API.set_error_message("Sem Sinal")
                                        error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                                        error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                        
                                        return
                                       
                         
                                TEST_CREATION_API.send_ir_rc_command("[OK]")
                                Install_image = NOS_API.wait_for_multiple_pictures(["Install_Success_ref"], 5, ["[SEARCH]"], [HDMI_Threshold])
                                if(Install_image != 0):
                                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                                Install_Success_image = NOS_API.wait_for_multiple_pictures(["Install_Success_ref","Install_Success_ref1"], 30, ["[SUCCESS_INSTALL]","[SUCCESS_INSTALL]"], [HDMI_Threshold,HDMI_Threshold])
                                
                                if(Install_Success_image == 0):
                                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                                    continue
                                else:
                                    TEST_CREATION_API.write_log_to_file("Signal value is lower than threshold") 
                                    TEST_CREATION_API.write_log_to_file("Falhou a meio da atualização")                                 
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                                    NOS_API.set_error_message("Sem Sinal")
                                    error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                                    error_messages = NOS_API.test_cases_results_info.input_signal_error_message
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return
                          
                                 
                        elif(signal_image == -1):
                            if(counter == 0):
                                NOS_API.display_custom_dialog("Confirme o cabo HDMI", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                                counter = counter +1
                                time.sleep(2)
                            else:
                                TEST_CREATION_API.write_log_to_file("Image is not reproduced correctly on HDMI.")
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message)
                                error_codes = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code
                                error_messages = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message
                                NOS_API.set_error_message("Video HDMI")
                                break
                        elif(boot_image == -2):
                        
                            if(counter == 1):
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                
                                return
                    
                            counter = counter +1
                            continue
            
    except Exception as error:
        test_result = "FAIL"
        TEST_CREATION_API.write_log_to_file(error)
        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.grabber_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.grabber_error_message)
        error_codes = NOS_API.test_cases_results_info.grabber_error_code
        error_messages = NOS_API.test_cases_results_info.grabber_error_message
        NOS_API.set_error_message("Inspection")
        
    NOS_API.add_test_case_result_to_file_report(
                    test_result,
                    "- - - - - - - - - - - - - - - - - - - -",
                    "- - - - - - - - - - - - - - - - - - - -",
                    error_codes,
                    error_messages)
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    report_file = ""
    if (test_result != "PASS"):
        report_file = NOS_API.create_test_case_log_file(
                        NOS_API.test_cases_results_info.s_n_using_barcode,
                        NOS_API.test_cases_results_info.nos_sap_number,
                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                        NOS_API.test_cases_results_info.mac_using_barcode,
                        end_time)
        NOS_API.upload_file_report(report_file)
        NOS_API.test_cases_results_info.isTestOK = False
        
        NOS_API.send_report_over_mqtt_test_plan(
                test_result,
                end_time,
                error_codes,
                report_file)
    
    
    ## Update test result
    TEST_CREATION_API.update_test_result(test_result)

    if(Hardware_Result):
        ## Return DUT to initial state and de-initialize grabber device
        NOS_API.deinitialize()
   