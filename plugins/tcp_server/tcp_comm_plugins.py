# -*- coding: utf-8 -*-
import sys, socket, threading
import logging
import time

from config import TcpRequestParser
from plugins.base_plugin import BasePlugin

class TaskStatusServer(threading.Thread):
    def __init__(self, name, server_address, num_of_connections, **kwargs):
        threading.Thread.__init__(self, name=name, kwargs=kwargs)
        self.setDaemon(True)
        self.server_address = server_address
        self.num_of_connections = num_of_connections
        self.started = False

        self.new_task_status_cond = threading.Condition()

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the socket to the port        
        print >> sys.stderr, '[Task-Status-Server] ... starting up on %s port %s' % self.server_address
        self.sock.bind(self.server_address)

        # Listen for incoming connections
        self.sock.listen(self.num_of_connections)

        self.connections = []

    def run(self):
        self.started = True
        while self.started:
            # Wait for a connection
            connection, client_address = self.sock.accept()
            print >>sys.stderr, '[Task-Status-Server] ... connection from: ', client_address
            if not connection in self.connections:
                self.connections.append(connection)
        self.started = False

    def sendTaskStatus(self, status):
        from xml.dom.minidom import Document
        doc = Document()
        root_element = doc.createElement("status")
        doc.appendChild(root_element)
        root_element.setAttribute("timeStamp", str(time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())))
        root_element.setAttribute("orderName", status[0])
        root_element.setAttribute("orderState", str(status[1]))
        if len(status) > 2:
            detail_element = doc.createElement("details")
            root_element.appendChild(detail_element)
            detail_element.appendChild(doc.createTextNode(str(status[2])))

        data = doc.toxml(encoding="utf-8")
        if self.connections:
            for connection in self.connections:
                try:
                    connection.sendall(data)
                except Exception, e:
                    connection.close()
                    self.connections.remove(connection)
                    
    def stop(self):
        self.started = False
        if self.connections:
            for connection in self.connections:
                # Clean up the connection
                try:
                    connection.close()
                except Exception, e:
                    pass
        self.sock.close()

class TaskOrderRequestHandler:
    def __init__(self, app):
        self.app = app
        self.request_parser = TcpRequestParser()

    """
    Response should NOT be None !!!
    """
    def handleRequest(self, request):
        response = None
        try:
            type = self.request_parser.parseRequestType(request)

            if type.upper() == "NC_DEVICE_LOADING_UNLOADING":
                orders = self.request_parser.parseNcOrderTask(request, "LOADING_UNLOADING")
                response = self.crateAndAddNewTask(orders)
            elif type.upper() == "NC_DEVICE_LOADING": # NC Devices (loading operation)
                orders = self.request_parser.parseNcOrderTask(request, "LOADING")
                response = self.crateAndAddNewTask(orders)
            elif type.upper() == "NC_DEVICE_UNLOADING":# NC Devices (unloading operation)
                orders = self.request_parser.parseNcOrderTask(request, "UNLOADING")
                response = self.crateAndAddNewTask(orders)
            elif type.upper() == "ROBOT_ASSEMBLE": # Robot Assemble Line
                orders = self.request_parser.parseRobotAssembleTask(request, "Robot Assemble")
                response = self.crateAndAddNewTask(orders)
            elif type.upper() == "TRIGGER": # Operation trigger
                order_name, device_no = self.request_parser.parseProductionOrderOperationTrigger(request)
                response = self.triggerBlockedTask(order_name, device_no)
            else:
                response = self.request_parser.parseDefaultType(type)
        except Exception, e:
            response = self.request_parser.createGeneralUnknownResponse(str(e))

        return response

    def crateAndAddNewTask(self, orders):
        try:
            new_task = self.app.createAndAddTask(orders)
        except Exception, e:
            return self.request_parser.createTaskResponse(False, str(e))
        return self.request_parser.createTaskResponse(True, new_task)

    def triggerBlockedTask(self, order_name, device_no):
        device_name = self.request_parser.getDeviceName(device_no)
        print("Trigger [{}] with device [{}] ....".format(order_name, device_name))
        self.app.triggerTask(order_name, device_name)
        return self.request_parser.createTaskTriggerSuccessResponse(order_name, device_name)

class TaskOrderServer(threading.Thread):
    def __init__(self, name, server_address, num_of_connections, request_handler, **kwargs):
        threading.Thread.__init__(self, name=name, kwargs=kwargs)
        self.setDaemon(True)
        self.server_address = server_address
        self.num_of_connections = num_of_connections
        self.request_handler = request_handler
        self.started = False

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the socket to the port        
        print >> sys.stderr, '[Task-Order-Server] ... starting up on %s port %s' % self.server_address
        self.sock.bind(self.server_address)

        # Listen for incoming connections
        self.sock.listen(self.num_of_connections)

    def handleRequest(self, request):
        response = self.request_handler.handleRequest(request)
        return response

    def run(self):
        self.started = True
        while self.started:
            # Wait for a connection
            connection, client_address = self.sock.accept()
            try:
                print >>sys.stderr, '[Task-Order-Server] ... connection from: ', client_address

                #while True:
                request = connection.recv(4096)
                print >>sys.stderr, '[Task-Order-Server] ... received "%s"' % request
                if request:
                    response = self.handleRequest(request)
                    if response:
                        connection.sendall(response)
                else:
                    print >>sys.stderr, '[Task-Order-Server] ... no data from', client_address
                    #break
            finally:
                # Clean up the connection
                connection.close()
        self.started = False

    def stop(self):
        self.started = False
        self.sock.close()

class TcpCommucation(BasePlugin):
    def __init__(self, app):
        BasePlugin.__init__(self, app)
        # host, port
        order_server_address = ('localhost', 11111)
        status_server_address = ('localhost', 11112)
        self.task_status_server = TaskStatusServer("Task-Status-Server-Thread",
                                                   status_server_address,
                                                   5)
        self.task_order_server = TaskOrderServer("Task-Order-Server-Thread", 
                                             order_server_address, 
                                             1,
                                             TaskOrderRequestHandler(app))

        #self.server = TcpServer(server_address, StreamRequestHandler)
        #self.task_order_server = threading.Thread(target=self.server.serve_forever)
        #self.task_order_server.setDaemon(True)
 
    def install(self):
        self.registerTaskMessageHandler(self.task_status_server.sendTaskStatus)
        self.task_status_server.start()
        self.task_order_server.start()
                
    def uninstall(self):
        self.unregisterTaskMessageHandler(self.task_status_server.sendTaskStatus)
        print "[Task-Status-Server] closing..."
        self.task_status_server.stop()        
        print "[Task-Order-Server] closing..."
        self.task_order_server.stop()
        #self.server.socket.close()