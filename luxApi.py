from flask import Flask
from flask_restful import Resource, Api, reqparse
from app import app

api = Api(app)
api.add_resource(clientData, '/api/v1/luxmdm')


class clientData(Resource):
    def get(self):
        pass  # return configuration commands, instructional commands

    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('serialnumber', type=str, required=True, location='json')
        parser.add_argument('osVersion', type=str, required=True, location='json')
        parser.add_argument('rootStatus', type=str, required=True, location='json')

        args = parser.parse_args(strict=True)
        deviceData = {'serial': args['serialnumber'], 'deviceos': args['os'], 'rootstatus': args['rootStatus']}

        return deviceData