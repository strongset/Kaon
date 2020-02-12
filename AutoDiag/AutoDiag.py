# -*- coding: utf-8 -*-
# Test name = Autodiag
# Test description = Autodiag

from datetime import datetime
from time import gmtime, strftime
import time

import TEST_CREATION_API
import NOS_API

USB_NOK = False
Descramble_NOK = False
Video_Decoding_NOK = False

def runTest():
    
    try:  
        ## Set test result default to FAIL
        test_result = "FAIL"
        
        error_codes = ""
        error_messages = ""
        global USB_NOK
        counter = 0
        ## Initialize grabber device
        TEST_CREATION_API.initialize_grabber()
        
        TEST_CREATION_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
        time.sleep(2)        
    
        while(counter < 2):
            ## Enter autodiag        
            TEST_CREATION_API.send_ir_rc_command("[ENTER_AUTODIAG]")
            
            AutoDiag_image = NOS_API.wait_for_multiple_pictures(["Autodiag_End_720_ref","Autodiag_End_refblack"], 45, ["[AUTODIAG_PROGRESS]","[AUTODIAG_PROGRESS]"], [TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD,TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD])
            if(AutoDiag_image == 0 or AutoDiag_image == 1):
                if not(NOS_API.grab_picture("AutoDiag_Result")):
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
                
                AutoDiag_result_ocr = TEST_CREATION_API.OCR_recognize_text("AutoDiag_Result", "[AUTODIAG_CODE]", "[KAON_FILTER]","AutoDiag_Result")

                if(VerifyAD(str(AutoDiag_result_ocr))):
                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                    time.sleep(1)
                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                    if(NOS_API.wait_for_no_signal_present(20)):
                        try:
                            NOS_API.configure_power_switch()
                            NOS_API.power_off()
                        except:
                            TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                        test_result = "PASS"
                        counter = 4
                    else:
                        TEST_CREATION_API.write_log_to_file("Factory Reset NOK") 
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.measure_boot_time_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.measure_boot_time_error_message)
                        NOS_API.set_error_message("Factory Reset")
                        error_codes = NOS_API.test_cases_results_info.measure_boot_time_error_code
                        error_messages = NOS_API.test_cases_results_info.measure_boot_time_error_message
                        counter = 4
            
                
                else:
                    if(counter == 0 and USB_NOK):
                        NOS_API.display_custom_dialog("Confirme o cabo USB", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                        time.sleep(2)
                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                    counter = counter + 1
                    continue
                    
                    if(Descramble_NOK):
                        TEST_CREATION_API.write_log_to_file("Descramble test fail")
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_descramble_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.hdmi_descramble_error_message)
                        NOS_API.set_error_message("Video HDMI(Não Retestar)")
                        error_codes = NOS_API.test_cases_results_info.hdmi_descramble_error_code
                        error_messages = NOS_API.test_cases_results_info.hdmi_descramble_error_message
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
                
                    if(Video_Decoding_NOK):
                        TEST_CREATION_API.write_log_to_file("Video Decoding test fail") 
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_video_decoding_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.hdmi_video_decoding_error_message)
                        NOS_API.set_error_message("Video HDMI(Não Retestar)")
                        error_codes = NOS_API.test_cases_results_info.hdmi_video_decoding_error_code
                        error_messages = NOS_API.test_cases_results_info.hdmi_video_decoding_error_message
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
                if(counter < 2):
                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                    counter = counter + 1
                    continue
                else:
                    if(AutoDiag_image == -1):
                        TEST_CREATION_API.write_log_to_file("Image is not reproduced correctly on HDMI.")
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_message)
                        error_codes = NOS_API.test_cases_results_info.hdmi_720p_noise_error_code
                        error_messages = NOS_API.test_cases_results_info.hdmi_720p_noise_error_message
                        NOS_API.set_error_message("Video HDMI")
                        
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
    
                    if(AutoDiag_image == -2):
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
                        
        if(counter == 2):
            TEST_CREATION_API.write_log_to_file("Autodiag failed")
            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.autodiag_error_code \
                                            + "; Error message: " + NOS_API.test_cases_results_info.autodiag_error_message)
            NOS_API.set_error_message("AutoDiag")
            error_codes = NOS_API.test_cases_results_info.autodiag_error_code
            error_messages = NOS_API.test_cases_results_info.autodiag_error_message
                                    
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
    
    
    
def VerifyAD(input_text):
    global USB_NOK
    global Descramble_NOK
    global Video_Decoding_NOK
    
    Result_OK = False
    result_decoding = False
    result_descramble = False
    result_USB = False
    result_ETH = False
    for i in range(len(input_text)):
        if(i==0):
            continue
        if(i==1):
            continue
        if(i==2):
            if(input_text[i] == "0"):
                result_decoding = True
                continue
            else:                
                Video_Decoding_NOK = True
                return False
            continue
        if(i==3):
            if(input_text[i] == "0"):
                result_descramble = True
                continue
            else:                
                Descramble_NOK = True
                return False
            continue    
        if(i==4):
            if(input_text[i] == "0"):
                result_USB = True
                continue
            else:
                if(USB_NOK):
                    TEST_CREATION_API.write_log_to_file("USB NOK") 
                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.usb_nok_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.usb_nok_error_message)
                    NOS_API.set_error_message("USB")
                    error_codes = NOS_API.test_cases_results_info.usb_nok_error_code
                    error_messages = NOS_API.test_cases_results_info.usb_nok_error_message
                USB_NOK = True
                return False
            continue
        if(i==5):
            result_ETH = True
            #if(input_text[i] == "0"):
            #    result_ETH = True
            #    continue
            #else:
            #    TEST_CREATION_API.write_log_to_file("Ethernet NOK") 
            #    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ethernet_nok_error_code \
            #                                    + "; Error message: " + NOS_API.test_cases_results_info.ethernet_nok_error_message)
            #    NOS_API.set_error_message("Eth")
            #    error_codes = NOS_API.test_cases_results_info.ethernet_nok_error_code
            #    error_messages = NOS_API.test_cases_results_info.ethernet_nok_error_message
            #    result_ETH = True # Tirar quando se definir o eth
            #    #return False
            continue
        if(i==6):
            continue
        if(i==7):
            continue
            
    if(result_decoding and result_descramble and result_USB and result_ETH):
        Result_OK = True
     
    return Result_OK
     