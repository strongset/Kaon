# Test name = Serial Number
# Test description = Check S/N from menu with scanned S/N, log nagraguide version and sw version
from datetime import datetime
import time

import TEST_CREATION_API
#import shutil
#shutil.copyfile('\\\\bbtfs\\RT-Executor\\API\\NOS_API.py', 'NOS_API.py')
import NOS_API

SNR_VALUE_THRESHOLD_LOW = 10
SNR_VALUE_THRESHOLD_HIGH = 21

BER_VALUE_THRESHOLD = "2.0E-6"

def runTest():
    System_Failure = 0
    
    while (System_Failure < 2):
        try:
            ## Set test result default to FAIL
            test_result = "FAIL"       
            SW = "-"
            SC = "-"
            MAC = "-"
            CASID = "-"
            Signal_HOR_Power = "-"
            Signal_VER_Power = "-"
            ber_hor_value = "-"
            ber_ver_value = "-"

            error_codes = ""
            error_messages = ""
            counter = 0
            FIRMWARE_VERSION_PROD = NOS_API.Firmware_Version_KAON
            
            ## Get scanned STB Barcode
            scanned_casid = NOS_API.test_cases_results_info.cas_id_using_barcode
            scanned_mac = NOS_API.test_cases_results_info.mac_using_barcode
    
            ## Initialize grabber device
            TEST_CREATION_API.initialize_grabber()

            ## Start grabber device with video on default video source
            TEST_CREATION_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
            time.sleep(3)
            if(System_Failure > 0):
                TEST_CREATION_API.send_ir_rc_command("[BACK]")
                TEST_CREATION_API.send_ir_rc_command("[BACK]")
            
            if (NOS_API.is_signal_present_on_video_source()):
                
                if(NOS_API.SET_720):
                    TEST_CREATION_API.send_ir_rc_command("[SET_RESOLUTION_1080]")
                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                    if (video_height != "1080"): 
                        TEST_CREATION_API.send_ir_rc_command("[SET_RESOLUTION_1080_2ndTry]")
                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                        if (video_height != "1080"):    
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.resolution_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.resolution_error_message)
                            error_codes = NOS_API.test_cases_results_info.resolution_error_code
                            error_messages = NOS_API.test_cases_results_info.resolution_error_message
                            NOS_API.set_error_message("Resolução")
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
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            return
                                            
                TEST_CREATION_API.send_ir_rc_command("[TECH_INFO]")     
                if not(NOS_API.grab_picture("Tech_info")):
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
                
                
                video_result = NOS_API.compare_pictures("Tech_info_ref", "Tech_info", "[TECH_MENU]")
                if(video_result < TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                    TEST_CREATION_API.send_ir_rc_command("[TECH_INFO]")
                    if not(NOS_API.grab_picture("Tech_info")):
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
                    
                    
                    video_result1 = NOS_API.compare_pictures("Tech_info_ref", "Tech_info", "[TECH_MENU]")
                    if(video_result < TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                        TEST_CREATION_API.write_log_to_file("Doesn't Navigate to right place")
                        NOS_API.set_error_message("Navegação")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                        error_codes = NOS_API.test_cases_results_info.navigation_error_code
                        error_messages = NOS_API.test_cases_results_info.navigation_error_message
                        NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
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
        
                
                MAC = fix(TEST_CREATION_API.OCR_recognize_text("Tech_info", "[MAC]", "[KAON_FILTER]","MAC"))
                SW = fix(TEST_CREATION_API.OCR_recognize_text("Tech_info", "[SW]", "[KAON_FILTER]","SW"))
                CAS_ID = fix(TEST_CREATION_API.OCR_recognize_text("Tech_info", "[CASID]", "[KAON_FILTER]","CASID"))
                IP = TEST_CREATION_API.OCR_recognize_text("Tech_info", "[IP]", "[KAON_FILTER]","IP")
                TEST_CREATION_API.write_log_to_file("MAC: " + str(MAC))
                TEST_CREATION_API.write_log_to_file("SW Version : " + str(SW)) 
                TEST_CREATION_API.write_log_to_file("Cas ID: " + str(CAS_ID))
                TEST_CREATION_API.write_log_to_file("IP: " + str(IP))
                
                
                video_result = NOS_API.compare_pictures("No_Card_ref", "Tech_info", "[SC]")
                if(video_result >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                    NOS_API.display_dialog("Reinsira o cart\xe3o e de seguida pressiona Continuar", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)                                           
                    TEST_CREATION_API.send_ir_rc_command("[REDO_SC]")
                    if not(NOS_API.grab_picture("SC_Retry")):
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
                    video_result1 = NOS_API.compare_pictures("No_Card_ref", "SC_Retry", "[SC]")
                    if(video_result1 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                    
                        TEST_CREATION_API.write_log_to_file("Smart card is not detected")
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.sc_not_detected_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.sc_not_detected_error_message)
                        NOS_API.set_error_message("SmartCard")
                        error_codes = NOS_API.test_cases_results_info.sc_not_detected_error_code
                        error_messages = NOS_API.test_cases_results_info.sc_not_detected_error_message 
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
                        SC = fix(TEST_CREATION_API.OCR_recognize_text("Tech_info", "[SC]","[KAON_FILTER]","SC"))
                        TEST_CREATION_API.write_log_to_file("Smartcard: " + str(SC)) 
                else:
                    SC = fix(TEST_CREATION_API.OCR_recognize_text("Tech_info", "[SC]","[KAON_FILTER]","SC"))
                    TEST_CREATION_API.write_log_to_file("Smartcard: " + str(SC)) 
                
                
                if not(str(MAC) == scanned_mac):
                    TEST_CREATION_API.write_log_to_file("MAC number is not the same as previous scanned mac number")
                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.wrong_mac_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.wrong_mac_error_message)
                    NOS_API.set_error_message("MAC")
                    error_codes = NOS_API.test_cases_results_info.wrong_mac_error_code
                    error_messages = NOS_API.test_cases_results_info.wrong_mac_error_message 
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
                if not(str(CAS_ID) == scanned_casid):
                    TEST_CREATION_API.write_log_to_file("CAS ID number and CAS ID number previuosly scanned by barcode scanner is not the same")
                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.wrong_cas_id_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.wrong_cas_id_error_message \
                                                            + "; OCR: " + str(cas_id_number))
                    NOS_API.set_error_message("CAS ID")
                    error_codes = NOS_API.test_cases_results_info.wrong_cas_id_error_code
                    error_messages = NOS_API.test_cases_results_info.wrong_cas_id_error_message
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
                if not(str(SW) == FIRMWARE_VERSION_PROD):
                    TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                    NOS_API.set_error_message("Não Actualiza") 
                    error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                    error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message 
                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
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
                if not(HasIP(IP)):
                    NOS_API.display_dialog("Confirme o cabo Eth", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)                                           
                    TEST_CREATION_API.send_ir_rc_command("[REDO_SC]")
                    if not(NOS_API.grab_picture("ETH_Retry")):
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
                
                
                    IP_2ndTry = TEST_CREATION_API.OCR_recognize_text("ETH_Retry", "[IP]", "[KAON_FILTER]","IP_2ndTry")

                    TEST_CREATION_API.write_log_to_file("IP Second Try: " + str(IP_2ndTry))
                
                    if not(HasIP(IP_2ndTry)):
                        TEST_CREATION_API.write_log_to_file("Ethernet NOK") 
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ethernet_nok_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.ethernet_nok_error_message)
                        NOS_API.set_error_message("Eth")
                        error_codes = NOS_API.test_cases_results_info.ethernet_nok_error_code
                        error_messages = NOS_API.test_cases_results_info.ethernet_nok_error_message
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
                    
                TEST_CREATION_API.send_ir_rc_command("[BACK]")
                TEST_CREATION_API.send_ir_rc_command("[Signal_INFO]")
                time.sleep(1)
                if not(NOS_API.grab_picture("Signal_Hor_info")):
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
                    
                video_result = NOS_API.compare_pictures("Signal_info_ref", "Signal_Hor_info", "[SIGNALMENU]")
                video_result1 = NOS_API.compare_pictures("Signal_info_ref", "Signal_Hor_info", "[SIGNALMENU_CHANNEL]")
                if(video_result < TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                    if(video_result1 < TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                        TEST_CREATION_API.send_ir_rc_command("[CH_3]")
                        
                    TEST_CREATION_API.send_ir_rc_command("[Signal_INFO_RETRY]")
                    if not(NOS_API.grab_picture("Signal_Hor_info")):
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
                    
                    
                    video_result1 = NOS_API.compare_pictures("Signal_info_ref", "Signal_Hor_info", "[SIGNALMENU]")
                    video_result1 = NOS_API.compare_pictures("Signal_info_ref", "Signal_Hor_info", "[SIGNALMENU_CHANNEL]")
                    if(video_result < TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                        TEST_CREATION_API.write_log_to_file("Doesn't Navigate to right place")
                        NOS_API.set_error_message("Navegação")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                        error_codes = NOS_API.test_cases_results_info.navigation_error_code
                        error_messages = NOS_API.test_cases_results_info.navigation_error_message
                        NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
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

                
                Signal_HOR_Power_OCR = TEST_CREATION_API.OCR_recognize_text("Signal_Hor_info", "[SNR]", "[KAON_FILTER]","Signal_HOR")            
                BER_HOR_OCR = change_ber(TEST_CREATION_API.OCR_recognize_text("Signal_Hor_info", "[BER]", "[KAON_FILTER]","BER_HOR"))
                try:    
                    Signal_HOR_Power = float(Signal_HOR_Power_OCR)
                    ber_hor_value = NOS_API.fix_ber(BER_HOR_OCR)
                    
                except:
                    Signal_HOR_Power = '-'
                    ber_hor_value = '-'
                    
                TEST_CREATION_API.write_log_to_file("Signal Hor: " + str(Signal_HOR_Power_OCR)) 
                TEST_CREATION_API.write_log_to_file("BER Hor: " + str(ber_hor_value))
                
                if(Signal_HOR_Power < 5 or Signal_HOR_Power > 21):
                    TEST_CREATION_API.write_log_to_file("Signal value is outside threshold limits")                            
                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                    NOS_API.set_error_message("Sem Sinal")
                    error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                    error_messages = NOS_API.test_cases_results_info.input_signal_error_message  
                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
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
            
        
                if not(NOS_API.check_ber(ber_hor_value, BER_VALUE_THRESHOLD)):
                    TEST_CREATION_API.write_log_to_file("BER value is lower than threshold")
                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ber_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.ber_error_message)
                    NOS_API.set_error_message("BER") 
                    
                    error_codes = NOS_API.test_cases_results_info.ber_error_code
                    error_messages = NOS_API.test_cases_results_info.ber_error_message
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
                
                
                
                TEST_CREATION_API.send_ir_rc_command("[VER_CH]")
                time.sleep(1.5)
                if not(NOS_API.grab_picture("Ver_CH_info")):
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
                
                time.sleep(1)
                
                if not(NOS_API.grab_picture("Ver_CH_info1")):
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
                
                
                
                Signal_VER_Power_OCR = fix_signal(TEST_CREATION_API.OCR_recognize_text("Ver_CH_info", "[SNR]", "[KAON_FILTER]","Signal_VER"))           
                BER_VER_OCR = change_ber(TEST_CREATION_API.OCR_recognize_text("Ver_CH_info", "[BER]", "[KAON_FILTER]","BER_VER"))
                try:
                    Signal_VER_Power = float(Signal_VER_Power_OCR)
                    ber_ver_value = NOS_API.fix_ber(BER_VER_OCR)
                except:
                    Signal_VER_Power = '-'
                    ber_ver_value = '-'
                    
                if(Signal_VER_Power < 10 or Signal_VER_Power == '-'):
                    Signal_VER_Power_OCR = fix_signal(TEST_CREATION_API.OCR_recognize_text("Ver_CH_info1", "[SNR]", "[KAON_FILTER]","Signal_VER"))           
                    BER_VER_OCR = change_ber(TEST_CREATION_API.OCR_recognize_text("Ver_CH_info1", "[BER]", "[KAON_FILTER]","BER_VER"))
                    try:
                        Signal_VER_Power = float(Signal_VER_Power_OCR)
                        ber_ver_value = NOS_API.fix_ber(BER_VER_OCR)
                    except:
                        Signal_VER_Power = '-'
                        ber_ver_value = '-'
                        
                    
                    
                TEST_CREATION_API.write_log_to_file("Signal Ver: " + str(Signal_VER_Power_OCR)) 
                TEST_CREATION_API.write_log_to_file("BER Ver: " + str(ber_ver_value))
                
                
                
                if(Signal_VER_Power < 5 or Signal_VER_Power > 21):
                    TEST_CREATION_API.write_log_to_file("Signal value is outside threshold limits")                            
                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                    NOS_API.set_error_message("Sem Sinal")
                    error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                    error_messages = NOS_API.test_cases_results_info.input_signal_error_message  
                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
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
            
        
                if not(NOS_API.check_ber(ber_ver_value, BER_VALUE_THRESHOLD)):
                    TEST_CREATION_API.write_log_to_file("BER value is lower than threshold")
                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ber_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.ber_error_message)
                    NOS_API.set_error_message("BER") 
                    
                    error_codes = NOS_API.test_cases_results_info.ber_error_code
                    error_messages = NOS_API.test_cases_results_info.ber_error_message
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
                
                
                
                TEST_CREATION_API.send_ir_rc_command("[CH_3]")
                time.sleep(2)
                TEST_CREATION_API.send_ir_rc_command("[BACK]")
                TEST_CREATION_API.send_ir_rc_command("[BACK]")
                TEST_CREATION_API.send_ir_rc_command("[BACK]")
                TEST_CREATION_API.send_ir_rc_command("[BACK]")
                test_result = "PASS"
        
            else:
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
            
            test = "PASS"

            System_Failure = 2
        except Exception as error:
            if(System_Failure == 0):
                System_Failure = System_Failure + 1 
                NOS_API.Inspection = True
                if(System_Failure == 1):
                    try:
                        TEST_CREATION_API.write_log_to_file(error)
                    except: 
                        pass
                    try:
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        TEST_CREATION_API.write_log_to_file(error)
                    except: 
                        pass
                if (NOS_API.configure_power_switch_by_inspection()):
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
                    time.sleep(10)
                    ## Power on STB with energenie
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
                        
                        test_result = "FAIL"
                        
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
                    time.sleep(10)
                else:
                    TEST_CREATION_API.write_log_to_file("Incorrect test place name")
                    
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_switch_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.power_switch_error_message)
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
                    
                    test_result = "FAIL"
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
                
                NOS_API.Inspection = False
            else:
                test_result = "FAIL"
                TEST_CREATION_API.write_log_to_file(error)
                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.grabber_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.grabber_error_message)
                error_codes = NOS_API.test_cases_results_info.grabber_error_code
                error_messages = NOS_API.test_cases_results_info.grabber_error_message
                NOS_API.set_error_message("Inspection")
                System_Failure = 2

    NOS_API.add_test_case_result_to_file_report(
                    test_result,
                    str(Signal_HOR_Power) + " " + str(ber_hor_value) + " - - - - - " + str(Signal_HOR_Power) + " " + str(ber_hor_value)  + " " +  str(Signal_VER_Power) + " " + str(ber_ver_value) + " - " + str(CASID) + " " + str(SW) + " - " + str(SC) + " - - - -",
                    "dB - - - - - - dB - dB - - - - - - - - - -",
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

    ## Return DUT to initial state and de-initialize grabber device
    NOS_API.deinitialize()
    
    
def fix(input_text):   
    output_text = input_text
    # Remove . from string
    if (":" in output_text):
        output_text = output_text.replace(':', '') 

    if (" " in output_text):
        output_text = output_text.replace(' ', '')
        
    if ("'" in output_text):
        output_text = output_text.replace('\'', '')
    if ("|" in output_text):
        output_text = output_text.replace('|', '1')
    if ("O" in output_text):
        output_text = output_text.replace('O', '0')
    if ("S" in output_text):
        output_text = output_text.replace('S', '5')
        
        
    return output_text.upper()

   
def change_ber(input_text):
    output_text = input_text
    
    if ("s" in output_text):
        output_text = output_text.replace('s', '5') 

    if ("S" in output_text):
        output_text = output_text.replace('S', '5') 

    if(output_text[output_text.find('E')-1] == '-'):
        output_text= output_text[:output_text.find('E')-1] + output_text[output_text.find('E'):]
        
    return output_text
  
def fix_signal(input_text):
    output_text = input_text
    
    if ("(" in output_text):
        output_text = output_text.replace('(', '0') 
    if ("!" in output_text):
        output_text = output_text.replace('!', '')     
    return output_text
  
def HasIP(input_text):
    if("10" in input_text):
        return True
    
    return False



  
  