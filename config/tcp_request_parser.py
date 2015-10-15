# -*- coding: utf-8 -*-
from xml.dom.minidom import Document
from xml.etree import ElementTree as ET

OPERATION_BLOCK = "__DEVICE_BLOCK__"

DEVICE_NAME_MAPPING = {
    1: "NC-Device-01",
    2: "NC-Device-02",
    3: "NC-Device-03",
    4: "NC-Device-04",
    5: "NC-Device-05",
    6: "NC-Device-06",
    11: "Robot-Device-11",
    12: "Robot-Device-12",
    13: "Robot-Device-13",
    14: "Robot-Device-14",
    15: "Robot-Device-15",
    16: "Robot-Device-16",
}

ROBOT_D5_LOADING_MAPPING = {
    1: 11,
    2: 12,
    3: 13,
    4: 14,
    5: 15,
    6: 16
}

ROBOT_D5_UNLOADING_MAPPING = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6
}

ROBOT_D6_NC_LOCK_MAPPING = {
    1: 15,
    2: 25,
    3: 35,
    4: 45,
    5: 55,
    6: 65
}

ROBOT_D6_NC_UNLOCK_MAPPING = {
    1: 11,
    2: 21,
    3: 31,
    4: 41,
    5: 51,
    6: 61
}

ROBOT_D7_UNLOADING_GRAB_COMPLETE_MAPPING = {
    1: 10,
    2: 20,
    3: 30,
    4: 40,
    5: 50,
    6: 60
}

ROBOT_D7_UNLOADING_LEAVE_COMPLETE_MAPPING = {
    1: 11,
    2: 21,
    3: 31,
    4: 41,
    5: 51,
    6: 61
}

ROBOT_D7_LOADING_PLACED_COMPLETE_MAPPING = {
    1: 15,
    2: 25,
    3: 35,
    4: 45,
    5: 55,
    6: 65
}

ROBOT_D7_LOADING_LEAVED_COMPLETE_MAPPING = {
    1: 16,
    2: 26,
    3: 36,
    4: 46,
    5: 56,
    6: 66
}

class TcpRequestParser:
    def __init__(self):
        pass

    ######################## NC DEVICES Start #############################
    def genOneNcLoadingOrders(self, nc_device_id, program_num):
        global DEVICE_NAME_MAPPING
        global ROBOT_D5_LOADING_MAPPING
        global ROBOT_D6_NC_LOCK_MAPPING
        global ROBOT_D7_LOADING_PLACED_COMPLETE_MAPPING
        global ROBOT_D7_LOADING_LEAVED_COMPLETE_MAPPING

        nc_device_name = DEVICE_NAME_MAPPING[nc_device_id]

        return [
            # NC
            (nc_device_name, "write_program_num", {'pronum-value': [program_num]}),
            (nc_device_name, "before_unclamp", {}),
            # ROBOT
            ("Robot-Device-01", "d8_robot_status_idle", {}),
            ("Robot-Device-01", "d5_loading_prepare", {'location-no': [ROBOT_D5_LOADING_MAPPING[nc_device_id]]}),
            ("Robot-Device-01", "d7_loading_robot_placed_complete",
             {'location-no': [ROBOT_D7_LOADING_PLACED_COMPLETE_MAPPING[nc_device_id]]}),
            # NC
            (nc_device_name, "before_clamp", {}),
            # ROBOT
            ("Robot-Device-01", "d8_robot_status_executing", {}),
            ("Robot-Device-01", "d6_loading_nc_lock", {'location-no': [ROBOT_D6_NC_LOCK_MAPPING[nc_device_id]]}),
            ("Robot-Device-01", "d7_loading_robot_leaved_complete",
             {'location-no': [ROBOT_D7_LOADING_LEAVED_COMPLETE_MAPPING[nc_device_id]]}),
            # NC ###
            (nc_device_name, "execute_program", {})
        ]

    def genOneNcUnloadingOrders(self, nc_device_id, program_num):
        global DEVICE_NAME_MAPPING
        global ROBOT_D5_UNLOADING_MAPPING
        global ROBOT_D6_NC_UNLOCK_MAPPING
        global ROBOT_D7_UNLOADING_GRAB_COMPLETE_MAPPING
        global ROBOT_D7_UNLOADING_LEAVE_COMPLETE_MAPPING

        nc_device_name = DEVICE_NAME_MAPPING[nc_device_id]

        return [
            # ROBOT
            ("Robot-Device-01", "d8_robot_status_idle", {}),
            ("Robot-Device-01", "d5_unloading_prepare", {'location-no': [ROBOT_D5_UNLOADING_MAPPING[nc_device_id]]}),
            ("Robot-Device-01", "d7_unloading_robot_grab_complete",
             {'location-no': [ROBOT_D7_UNLOADING_GRAB_COMPLETE_MAPPING[nc_device_id]]}),
            # NC
            (nc_device_name, "after_unclamp", {}),
            # ROBOT
            ("Robot-Device-01", "d8_robot_status_executing", {}),
            ("Robot-Device-01", "d6_unloading_nc_unlock", {'location-no': [ROBOT_D6_NC_UNLOCK_MAPPING[nc_device_id]]}),
            ("Robot-Device-01", "d7_unloading_robot_leaved_complete",
             {'location-no': [ROBOT_D7_UNLOADING_LEAVE_COMPLETE_MAPPING[nc_device_id]]}),
            # NC
            (nc_device_name, "after_clamp", {}),
            # ROBOT
            ("Robot-Device-01", "d8_robot_status_idle", {})
        ]

    def genOneNcLoadingAndUnloadingOrders(self, nc_device_id, program_num):
        orders = self.genOneNcLoadingOrders(nc_device_id, program_num)
        unloading_orders = self.genOneNcUnloadingOrders(nc_device_id, program_num)
        orders.extend(unloading_orders)
        return orders
        # global DEVICE_NAME_MAPPING
        # global ROBOT_D5_LOADING_MAPPING
        # global ROBOT_D5_UNLOADING_MAPPING
        # global ROBOT_D6_NC_LOCK_MAPPING
        # global ROBOT_D6_NC_UNLOCK_MAPPING
        # global ROBOT_D7_UNLOADING_GRAB_COMPLETE_MAPPING
        # global ROBOT_D7_UNLOADING_LEAVE_COMPLETE_MAPPING
        # global ROBOT_D7_LOADING_PLACED_COMPLETE_MAPPING
        # global ROBOT_D7_LOADING_LEAVED_COMPLETE_MAPPING
        #
        # nc_device_name = DEVICE_NAME_MAPPING[nc_device_id]
        #
        # return [
        #     # NC
        #     (nc_device_name, "write_program_num", {'pronum-value': [program_num]}),
        #     (nc_device_name, "before_unclamp", {}),
        #     # ROBOT
        #     ("Robot-Device-01", "d8_robot_status_idle", {}),
        #     ("Robot-Device-01", "d5_loading_prepare", {'location-no': [ROBOT_D5_LOADING_MAPPING[nc_device_id]]}),
        #     ("Robot-Device-01", "d7_loading_robot_placed_complete",
        #      {'location-no': [ROBOT_D7_LOADING_PLACED_COMPLETE_MAPPING[nc_device_id]]}),
        #     # NC
        #     (nc_device_name, "before_clamp", {}),
        #     # ROBOT
        #     ("Robot-Device-01", "d8_robot_status_executing", {}),
        #     ("Robot-Device-01", "d6_loading_nc_lock", {'location-no': [ROBOT_D6_NC_LOCK_MAPPING[nc_device_id]]}),
        #     ("Robot-Device-01", "d7_loading_robot_leaved_complete",
        #      {'location-no': [ROBOT_D7_LOADING_LEAVED_COMPLETE_MAPPING[nc_device_id]]}),
        #     # NC ###
        #     (nc_device_name, "execute_program", {}),
        #     # ROBOT
        #     ("Robot-Device-01", "d8_robot_status_idle", {}),
        #     ("Robot-Device-01", "d5_unloading_prepare", {'location-no': [ROBOT_D5_UNLOADING_MAPPING[nc_device_id]]}),
        #     ("Robot-Device-01", "d7_unloading_robot_grab_complete",
        #      {'location-no': [ROBOT_D7_UNLOADING_GRAB_COMPLETE_MAPPING[nc_device_id]]}),
        #     # NC
        #     (nc_device_name, "after_unclamp", {}),
        #     # ROBOT
        #     ("Robot-Device-01", "d8_robot_status_executing", {}),
        #     ("Robot-Device-01", "d6_unloading_nc_unlock", {'location-no': [ROBOT_D6_NC_UNLOCK_MAPPING[nc_device_id]]}),
        #     ("Robot-Device-01", "d7_unloading_robot_leaved_complete",
        #      {'location-no': [ROBOT_D7_UNLOADING_LEAVE_COMPLETE_MAPPING[nc_device_id]]}),
        #     # NC
        #     (nc_device_name, "after_clamp", {}),
        #     # ROBOT
        #     ("Robot-Device-01", "d8_robot_status_idle", {})
        # ]

    def parseNcOrderTask(self, request, operation = "LOADING_UNLOADING"):
        orders = []

        gen_func = {"LOADING": self.genOneNcLoadingOrders,
                    "UNLOADING": self.genOneNcUnloadingOrders,
                    "LOADING_UNLOADING": self.genOneNcLoadingAndUnloadingOrders}
        if not operation in gen_func.keys():
            raise Exception("Unknown operation [{}]".format(operation))

        root = ET.fromstring(request)
        node_workorder_iter = root.getiterator("workorder")
        for node_workorder in node_workorder_iter:
            device_no = eval(node_workorder.attrib.get('device'))
            program_no = eval(node_workorder.attrib.get('program_no'))

            for order in gen_func[operation.upper()](device_no, program_no):
                orders.append(order)

        return orders

    def parseRobotAssembleTask(self, request, operation):
        root = ET.fromstring(request)
        device_id = eval(root.attrib.get('device'))

        return [
            (DEVICE_NAME_MAPPING[device_id], OPERATION_BLOCK, {}),
            (DEVICE_NAME_MAPPING[device_id],  "write_vehicle_arrived_status", {}),
            (DEVICE_NAME_MAPPING[device_id],  "read_vehicle_arrived_status", {})
        ]

    ######################## NC DEVICES End #############################

    ######################## Operation Trigger Start #############################
    def parseProductionOrderOperationTrigger(self, request):
        root = ET.fromstring(request)

        node_trigger = root.find("workorderTrigger")
        order_name = node_trigger.attrib.get('task')
        device_no = eval(node_trigger.attrib.get('device'))
        return order_name, device_no

    ######################## Operation Trigger End #############################


    ######################## Default Type Start #############################
    def parseDefaultType(self, type):
        raise Exception("The type [{}] is not recognized".format(type))

    ######################## Default Type End #############################

    def parseRequestType(self, request):
        request_type = "DEFAULT"
        try:
            root = ET.fromstring(request)
            request_type = root.attrib.get("type").upper()
        except Exception, e:
            pass

        return request_type

    """
   =========================== RESPONSE ===========================
   """

    def createTaskResponse(self, status, message):
        doc = Document()
        root_response = doc.createElement('ProductionResponse')
        root_response.setAttribute("creationSuccessful", str(status))
        if status:
            task = message
            root_response.setAttribute("orderName", task.name)
            for order in task.orders:
                order_element = doc.createElement('order')
                order_element.appendChild(doc.createTextNode(str(order)))
                root_response.appendChild(order_element)
        else:
            root_response.setAttribute("reason", message)
        doc.appendChild(root_response)
        return doc.toxml(encoding='utf-8')

    def createTaskTriggerSuccessResponse(self, order_name, device_name):
        doc = Document()
        root_response = doc.createElement('ProductionTriggerResponse')
        root_response.setAttribute("creationSuccessful", str(True))
        root_response.setAttribute("orderName", order_name)
        root_response.setAttribute("deviceName", device_name)
        doc.appendChild(root_response)
        return doc.toxml(encoding='utf-8')

    def createGeneralUnknownResponse(self, message):
        doc = Document()
        root_response = doc.createElement('Response')
        root_response.setAttribute("creationSuccessful", str(False))
        root_response.setAttribute("reason", message)
        doc.appendChild(root_response)
        return doc.toxml(encoding='utf-8')

    def getDeviceName(self, device_id):
        # return "Robot-Device-01"
        return DEVICE_NAME_MAPPING[device_id]

    '''
    def parse(self, request):
        orders = []

        try:
            root = ET.fromstring(request)
            type = root.attrib.get("type")
            if type == "": # TODO
                orders = self.parseNcOrderTask(root)
            elif type == "": # TODO:
                orders = self.parseProductionOrderOperationTrigger(root)
            else:
                orders = self.parseProductionOrderDefault(root)
        except:
            raise Exception("Unknown command")

        return orders
    '''
