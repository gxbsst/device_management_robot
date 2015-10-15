# -*- coding: utf-8 -*-
from xml.dom.minidom import Document
from config import TcpRequestParser

class TaskOrderRequestParser:
    def __init__(self):
        self.request_parser = TcpRequestParser()

    def getType(self, request):
        return  self.request_parser.parseRequestType(request)

    def parseRequest(self, request):
        return self.request_parser.parse(request)

    def handleDefaultRequestType(self, request):
        self.request_parser.parseDefaultType()

    def createResponse(self, status, messsage):
        doc = Document()
        root_response = doc.createElement('ProductionResponse')
        root_response.setAttribute("creationSuccessful", str(status))
        if status:
            task = messsage
            root_response.setAttribute("orderName", task.name)
            for order in task.orders:
                order_element = doc.createElement('order')
                order_element.appendChild(doc.createTextNode(str(order)))
                root_response.appendChild(order_element)
        else:
            root_response.setAttribute("reason", messsage)
        doc.appendChild(root_response)
        return doc.toxml(encoding='utf-8')

