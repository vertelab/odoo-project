# -*- coding: UTF-8 -*-

################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import json
import logging
import werkzeug.wrappers
import datetime
import time
from odoo.http import request
import functools

_logger = logging.getLogger(__name__)


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if isinstance(o, bytes):
        return str(o)


def validate(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        try:
            client_secret = request.httprequest.args['client_secret']
            if not client_secret:
                raise
        except:
            return invalid_response("missing_client_secret",
                                    "client_secret is missing",
                                    403)
        try:
            client_id = request.httprequest.args['client_id']
            if not client_id:
                raise
        except:
            return invalid_response(
                "ACCESS ERROR",
                "Missing access token in request header.", 403)
        required_params = [
            'AF-TrackingId',
            'AF-SystemId',
            'AF-Environment',
        ]
        headers = request.httprequest.headers
        missed_params = []
        for param in required_params:
            if not headers.get(param):
                missed_params.append(param)
        if missed_params:
            return invalid_response(
                "Bad Request",
                "Missed headers params: %s" % ','.join(missed_params), 403)
        return func(self, *args, **kwargs)

    return wrap


def get_headers():
    response_header = request.httprequest.headers
    headers = {"AF-TrackingId": response_header.get('AF-TrackingId'),
               "AF-SystemId": response_header.get('AF-SystemId'),
               "AF-ResponseTime": int(round(time.time() * 1000)),
               "AF-Confidentiality": '1',
               "AF-Correctness": '2',
               "AF-Availability": '3',
               "AF-Traceability": '4',
               "AF-EndUserId": '5',
               "x-amf-mediaType": "application/json"}
    return headers


def valid_response(data=None, status=200, **kwargs):
    """Valid Response
    This will be return when the http request was successfully processed."""
    if not data:
        data = {}
    data.update({"message": "Successful execution of request."}, **kwargs)

    response = werkzeug.wrappers.Response(
        status=status,
        headers=get_headers(),
        content_type="application/json; charset=utf-8",
        response=json.dumps(data, default=default))
    return response


def invalid_response(error, message=None, status=400):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server.
    :param error: string
    :param message: string
    :param status: integer
    """
    payload = get_payload(status, error, message)

    response = werkzeug.wrappers.Response(
        status=status,
        headers=get_headers(),
        content_type="application/json; charset=utf-8",
        response=json.dumps(
            payload, default=datetime.datetime.isoformat))
    return response


def get_payload(status, typ, message):
    if status == 403:
        return {
            "error": typ,
            "description": message
        }
    else:
        return {
            "error_id": "77506961-60e4-42be-aff6-123ca6d4eea3",
            "message": typ,
            "cause": {
                "system": "EIS",
                "code": "1002",
                "message": message and str(
                    message) or "Wrong arguments (missing validation)",
                "error": [
                    {
                        "falt": None,
                        "felkod": 1002,
                        "operation": None,
                        "kravnummer": None,
                        "meddelande": message and str(
                            message) or "Wrong arguments (missing validation)",
                        "valideringsregelTyp": None,
                        "valideringsregelvarde": None,
                        "entitetTyp": None,
                        "entitetId": None
                    }
                ]
            }
        }


def get_example_data_xml():
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<ns146:ListaTjanstekategoriSvarsmeddelande xmlns:ns244=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaomfattningskategorianrop/v13\" xmlns:ns243=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaartikeltaxaanrop/v17\" xmlns:ns242=\"http://arbetsformedlingen.se/tjansteleverantor/request/listapristypanrop/v17\" xmlns:ns241=\"http://arbetsformedlingen.se/tjansteleverantor/request/listamiadefinitiontypanrop/v17\" xmlns:ns240=\"http://arbetsformedlingen.se/tjansteleverantor/request/listafelmeddelandenanrop/v9\" xmlns:ns239=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatendsignstatustypanrop/v15\" xmlns:ns238=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaetiketteranrop/v11\" xmlns:ns237=\"http://arbetsformedlingen.se/tjansteleverantor/request/listayrkesinriktninganrop/v1\" xmlns:ns236=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatolktekniskstatustypanrop/v17\" xmlns:ns235=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatillfalletypanrop/v17\" xmlns:ns234=\"http://arbetsformedlingen.se/tjansteleverantor/request/listasparersattningsomfattningtypanrop/v17\" xmlns:ns233=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatolknivaanrop/v15\" xmlns:ns232=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaapplikationsrollanrop/v17\" xmlns:ns231=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaskyddsklassanrop/v7\" xmlns:ns230=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaantagningsformanrop/v6\" xmlns:ns229=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatolkbokningstatustypanrop/v15\" xmlns:ns228=\"http://arbetsformedlingen.se/tjansteleverantor/request/listamomssatsanrop/v7\" xmlns:ns227=\"http://arbetsformedlingen.se/tjansteleverantor/request/listasprakstodanrop/v15\" xmlns:ns226=\"http://arbetsformedlingen.se/tjansteleverantor/request/listabegartstatustypanrop/v9\" xmlns:ns225=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaintegrationsinformationforleverantoranrop/v17\" xmlns:ns224=\"http://arbetsformedlingen.se/tjansteleverantor/request/listachecklistradforansokananrop/v6\" xmlns:ns223=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatidsenhetanrop/v2\" xmlns:ns222=\"http://arbetsformedlingen.se/tjansteleverantor/request/listalangdtypanrop/v13\" xmlns:ns221=\"http://arbetsformedlingen.se/tjansteleverantor/request/listamiadefinitiongruppanrop/v17\" xmlns:ns220=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaallatjansteranrop/v9\" xmlns:ns219=\"http://arbetsformedlingen.se/tjansteleverantor/request/listautbildningssattanrop/v6\" xmlns:ns218=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaersattningsomfattningaranrop/v10\" xmlns:ns217=\"http://arbetsformedlingen.se/tjansteleverantor/request/listasprakanrop/v1\" xmlns:ns216=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaersattningsomfattningstyperanrop/v10\" xmlns:ns215=\"http://arbetsformedlingen.se/tjansteleverantor/request/listastudietaktanrop/v16\" xmlns:ns214=\"http://arbetsformedlingen.se/tjansteleverantor/request/listasprakavvikelseanrop/v17\" xmlns:ns213=\"http://arbetsformedlingen.se/tjansteleverantor/request/listamiametadefinitioneranrop/v9\" xmlns:ns212=\"http://arbetsformedlingen.se/tjansteleverantor/request/listabankkontotypanrop/v0\" xmlns:ns211=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatjanstetypanrop/v16\" xmlns:ns210=\"http://arbetsformedlingen.se/tjansteleverantor/request/listamiadefinitiongruppregelanrop/v17\" xmlns:ns209=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaersattningstypkodanrop/v16\" xmlns:ns208=\"http://arbetsformedlingen.se/tjansteleverantor/request/listayrkesomradenanrop/v6\" xmlns:ns207=\"http://arbetsformedlingen.se/tjansteleverantor/request/listagranskningtypanrop/v13\" xmlns:ns206=\"http://arbetsformedlingen.se/tjansteleverantor/request/listamalgruppanrop/v6\" xmlns:ns205=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatolkbokninghandelsetypanrop/v17\" xmlns:ns204=\"http://arbetsformedlingen.se/tjansteleverantor/request/listastatustypanrop/v3\" xmlns:ns203=\"http://arbetsformedlingen.se/tjansteleverantor/request/listautbildningstypanrop/v6\" xmlns:ns202=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaveckodaganrop/v8\" xmlns:ns201=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaavvikelseorsakanrop/v15\" xmlns:ns200=\"http://arbetsformedlingen.se/tjansteleverantor/request/listasokparametraranrop/v7\" xmlns:ns199=\"http://arbetsformedlingen.se/tjansteleverantor/request/listamiaprisdefinitiontypanrop/v17\" xmlns:ns198=\"http://arbetsformedlingen.se/tjansteleverantor/request/listautbildningsformanrop/v6\" xmlns:ns197=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaavropstypanrop/v13\" xmlns:ns196=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatolktypanrop/v15\" xmlns:ns195=\"http://arbetsformedlingen.se/tjansteleverantor/request/listabetalmodelltypanrop/v13\" xmlns:ns194=\"http://arbetsformedlingen.se/tjansteleverantor/request/listauppfoljningskategorianrop/v0\" xmlns:ns193=\"http://arbetsformedlingen.se/tjansteleverantor/request/listakonfigureringanrop/v17\" xmlns:ns192=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaservicemodultypanrop/v16\" xmlns:ns191=\"http://arbetsformedlingen.se/tjansteleverantor/request/hamtaversionanrop/v9\" xmlns:ns190=\"http://arbetsformedlingen.se/tjansteleverantor/request/listamodulprisenhetanrop/v6\" xmlns:ns189=\"http://arbetsformedlingen.se/tjansteleverantor/request/listautbildningsklassanrop/v7\" xmlns:ns188=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaalternativortpristypanrop/v17\" xmlns:ns187=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatolkanvandareanrop/v16\" xmlns:ns186=\"http://arbetsformedlingen.se/tjansteleverantor/request/listakapiteldefinitioneranrop/v3\" xmlns:ns185=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatolktaxaanrop/v17\" xmlns:ns184=\"http://arbetsformedlingen.se/tjansteleverantor/request/listainkopsorderprocessanrop/v17\" xmlns:ns183=\"http://arbetsformedlingen.se/tjansteleverantor/request/listamodultypanrop/v16\" xmlns:ns182=\"http://arbetsformedlingen.se/tjansteleverantor/request/pinganrop/v17\" xmlns:ns181=\"http://arbetsformedlingen.se/tjansteleverantor/request/listabetalningsvillkoranrop/v17\" xmlns:ns180=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatjanstekategorianrop/v6\" xmlns:ns179=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaavvikelsetypanrop/v15\" xmlns:ns178=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaresurskonanrop/v15\" xmlns:ns177=\"http://arbetsformedlingen.se/tjansteleverantor/request/listakontaktpersontypanrop/v16\" xmlns:ns176=\"http://arbetsformedlingen.se/tjansteleverantor/request/listadistanstolktypanrop/v17\" xmlns:ns175=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaartikeltypanrop/v17\" xmlns:ns174=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatjanstanrop/v0\" xmlns:ns173=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatolkanvandaresvar/v16\" xmlns:ns172=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tolkanvandare/v16\" xmlns:ns171=\"http://arbetsformedlingen.se/tjansteleverantor/response/listayrkesgrupperperyrkesomradesvar/v6\" xmlns:ns170=\"http://arbetsformedlingen.se/tjansteleverantor/request/listayrkesgrupperperyrkesomradeanrop/v6\" xmlns:ns169=\"http://arbetsformedlingen.se/tjansteleverantor/response/listastudietaktsvar/v16\" xmlns:ns168=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/studietakt/v16\" xmlns:ns167=\"http://arbetsformedlingen.se/tjansteleverantor/response/listamiametadefinitionersvar/v9\" xmlns:ns166=\"http://arbetsformedlingen.se/tjansteleverantor/response/listayrkesomradensvar/v6\" xmlns:ns165=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatolktaxasvar/v17\" xmlns:ns164=\"http://arbetsformedlingen.se/tjansteleverantor/response/listafelmeddelandensvar/v9\" xmlns:ns163=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatjanstforkategorisvar/v17\" xmlns:ns162=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatjanstforkategorianrop/v6\" xmlns:ns161=\"http://arbetsformedlingen.se/tjansteleverantor/response/listakontaktpersontypsvar/v16\" xmlns:ns160=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/kontaktpersontyp/v16\" xmlns:ns159=\"http://arbetsformedlingen.se/tjansteleverantor/response/listautbildningstypsvar/v6\" xmlns:ns158=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/utbildningstyp/v6\" xmlns:ns157=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaallatjanstersvar/v17\" xmlns:ns156=\"http://arbetsformedlingen.se/tjansteleverantor/response/listagranskningtypsvar/v13\" xmlns:ns155=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/granskningtyp/v13\" xmlns:ns154=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatolkbokninghandelsetypsvar/v17\" xmlns:ns153=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tolkbokninghandelsetyp/v17\" xmlns:ns152=\"http://arbetsformedlingen.se/tjansteleverantor/response/hamtayrkesgruppforutbildningarsvar/v6\" xmlns:ns151=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/yrkesgruppforutbildning/v6\" xmlns:ns150=\"http://arbetsformedlingen.se/tjansteleverantor/request/hamtayrkesgruppforutbildningaranrop/v6\" xmlns:ns149=\"http://arbetsformedlingen.se/tjansteleverantor/response/listasokparametrarsvar/v7\" xmlns:ns148=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatolktekniskstatustypsvar/v17\" xmlns:ns147=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tolkteknisktatustyp/v17\" xmlns:ns146=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatjanstekategorisvar/v17\" xmlns:ns145=\"http://arbetsformedlingen.se/tjansteleverantor/response/listamiadefinitiontypsvar/v17\" xmlns:ns144=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/miadefinitiontyp/v17\" xmlns:ns143=\"http://arbetsformedlingen.se/tjansteleverantor/response/pingsvar/v17\" xmlns:ns142=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaveckodagsvar/v8\" xmlns:ns141=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/veckodag/v8\" xmlns:ns140=\"http://arbetsformedlingen.se/tjansteleverantor/response/hamtayrkesomradeforutbildningarsvar/v6\" xmlns:ns139=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/yrkesomradeforutbildning/v6\" xmlns:ns138=\"http://arbetsformedlingen.se/tjansteleverantor/request/hamtayrkesomradeforutbildningaranrop/v6\" xmlns:ns137=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaservicemodultypsvar/v16\" xmlns:ns136=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/servicemodultyp/v16\" xmlns:ns135=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaavvikelsetypsvar/v15\" xmlns:ns134=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/avvikelsetyp/v15\" xmlns:ns133=\"http://arbetsformedlingen.se/tjansteleverantor/response/listasprakavvikelsesvar/v17\" xmlns:ns132=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/sprakavvikelse/v17\" xmlns:ns131=\"http://arbetsformedlingen.se/tjansteleverantor/response/listachecklistradforansokansvar/v6\" xmlns:ns130=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/checklistradforansokan/v6\" xmlns:ns129=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaintegrationsinformationforleverantorsvar/v17\" xmlns:ns128=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/integrationsinformationforleverantor/v17\" xmlns:ns127=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaavropstypsvar/v13\" xmlns:ns126=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/avropstyp/v13\" xmlns:ns125=\"http://arbetsformedlingen.se/tjansteleverantor/response/listalangdtypsvar/v13\" xmlns:ns124=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/langdtyp/v13\" xmlns:ns123=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaartikeltaxasvar/v17\" xmlns:ns122=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaantagningsformsvar/v6\" xmlns:ns121=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/antagningsform/v6\" xmlns:ns120=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaleveransomradesvar/v7\" xmlns:ns119=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaleveransomradeanrop/v7\" xmlns:ns118=\"http://arbetsformedlingen.se/tjansteleverantor/response/hamtatextsvar/v13\" xmlns:ns117=\"http://arbetsformedlingen.se/tjansteleverantor/request/hamtatextanrop/v13\" xmlns:ns116=\"http://arbetsformedlingen.se/tjansteleverantor/response/listapristypsvar/v17\" xmlns:ns115=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/pristyp/v17\" xmlns:ns114=\"http://arbetsformedlingen.se/tjansteleverantor/response/listautbildningsklasssvar/v7\" xmlns:ns113=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/utbildningsklass/v7\" xmlns:ns112=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaartikeltypsvar/v17\" xmlns:ns111=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatolknivasvar/v15\" xmlns:ns110=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaskyddsklasssvar/v7\" xmlns:ns109=\"http://arbetsformedlingen.se/tjansteleverantor/response/listamiaprisdefinitiontypsvar/v17\" xmlns:ns108=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatolkbokningstatustypsvar/v15\" xmlns:ns107=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tolkbokningstatustyp/v15\" xmlns:ns106=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaomfattningskategorisvar/v13\" xmlns:ns105=\"http://arbetsformedlingen.se/tjansteleverantor/response/hamtaversionsvar/v9\" xmlns:ns104=\"http://arbetsformedlingen.se/tjansteleverantor/response/listastatustypsvar/v3\" xmlns:ns103=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/statustyp/v3\" xmlns:ns102=\"http://arbetsformedlingen.se/tjansteleverantor/response/listabankkontotypsvar/v0\" xmlns:ns101=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/bankkontotyp/v0\" xmlns:ns100=\"http://arbetsformedlingen.se/tjansteleverantor/response/listakapiteldefinitionersvar/v3\" xmlns:ns99=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/kapiteldefinition/v3\" xmlns:ns98=\"http://arbetsformedlingen.se/tjansteleverantor/response/listamomssatssvar/v7\" xmlns:ns97=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatendsignstatustypsvar/v15\" xmlns:ns96=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tendsignstatustyp/v15\" xmlns:ns95=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaspraksvar/v1\" xmlns:ns94=\"http://arbetsformedlingen.se/tjansteleverantor/response/listasparersattningsomfattningtypsvar/v17\" xmlns:ns93=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/sparersattningsomfattningtyp/v17\" xmlns:ns92=\"http://arbetsformedlingen.se/tjansteleverantor/response/hamtabetalningsmodellsvar/v16\" xmlns:ns91=\"http://arbetsformedlingen.se/tjansteleverantor/request/hamtabetalningsmodellanrop/v9\" xmlns:ns90=\"http://arbetsformedlingen.se/tjansteleverantor/response/listamiadefinitiongruppsvar/v17\" xmlns:ns89=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/miadefinitiongrupp/v17\" xmlns:ns88=\"http://arbetsformedlingen.se/tjansteleverantor/response/listamodultypsvar/v16\" xmlns:ns87=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/modultyp/v16\" xmlns:ns86=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaersattningsomfattningarsvar/v13\" xmlns:ns85=\"http://arbetsformedlingen.se/tjansteleverantor/response/listamalgruppsvar/v6\" xmlns:ns84=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/malgrupp/v6\" xmlns:ns83=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaavvikelseorsaksvar/v15\" xmlns:ns82=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/avvikelseorsak/v15\" xmlns:ns81=\"http://arbetsformedlingen.se/tjansteleverantor/response/listasprakstodsvar/v15\" xmlns:ns80=\"http://arbetsformedlingen.se/tjansteleverantor/response/listabetalmodelltypsvar/v13\" xmlns:ns79=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/betalmodelltyp/v13\" xmlns:ns78=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatatortsvar/v0\" xmlns:ns77=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatatortanrop/v0\" xmlns:ns76=\"http://arbetsformedlingen.se/tjansteleverantor/response/listayrkesinriktningsvar/v1\" xmlns:ns75=\"http://arbetsformedlingen.se/tjansteleverantor/response/listainkopsorderprocesssvar/v17\" xmlns:ns74=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/inkopsorderprocess/v17\" xmlns:ns73=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaersattningsomfattningstypersvar/v10\" xmlns:ns72=\"http://arbetsformedlingen.se/tjansteleverantor/response/listabegartstatustypsvar/v9\" xmlns:ns71=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaersattningstypkodsvar/v16\" xmlns:ns70=\"http://arbetsformedlingen.se/tjansteleverantor/response/listautbildningssattsvar/v6\" xmlns:ns69=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/utbildningssatt/v6\" xmlns:ns68=\"http://arbetsformedlingen.se/tjansteleverantor/response/listabetalningsvillkorsvar/v17\" xmlns:ns67=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/betalningsvillkor/v17\" xmlns:ns66=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaapplikationsrollsvar/v17\" xmlns:ns65=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatidsenhetsvar/v2\" xmlns:ns64=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatillfalletypsvar/v17\" xmlns:ns63=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tillfalletyp/v17\" xmlns:ns62=\"http://arbetsformedlingen.se/tjansteleverantor/response/listautbildningsformsvar/v6\" xmlns:ns61=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/utbildningsform/v6\" xmlns:ns60=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatjanstetypsvar/v16\" xmlns:ns59=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tjanstetyp/v16\" xmlns:ns58=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaresurskonsvar/v15\" xmlns:ns57=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/resurskon/v15\" xmlns:ns56=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatextersvar/v13\" xmlns:ns55=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/text/v13\" xmlns:ns54=\"http://arbetsformedlingen.se/tjansteleverantor/request/listatexteranrop/v13\" xmlns:ns53=\"http://arbetsformedlingen.se/tjansteleverantor/response/listadistanstolktypsvar/v17\" xmlns:ns52=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/distanstolktyp/v17\" xmlns:ns51=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatolktypsvar/v15\" xmlns:ns50=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tolktyp/v15\" xmlns:ns49=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaalternativortpristypsvar/v17\" xmlns:ns48=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/alternativortpristyp/v17\" xmlns:ns47=\"http://arbetsformedlingen.se/tjansteleverantor/response/listakonfigureringsvar/v17\" xmlns:ns46=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/konfigurering/v17\" xmlns:ns45=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaetikettersvar/v11\" xmlns:ns44=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/etikett/v11\" xmlns:ns43=\"http://arbetsformedlingen.se/tjansteleverantor/response/listatjanstsvar/v17\" xmlns:ns42=\"http://arbetsformedlingen.se/tjansteleverantor/response/listamiadefinitiongruppregelsvar/v17\" xmlns:ns41=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/miadefinitiongruppregel/v17\" xmlns:ns40=\"http://arbetsformedlingen.se/tjansteleverantor/response/listamodulprisenhetsvar/v14\" xmlns:ns39=\"http://arbetsformedlingen.se/tjansteleverantor/response/listaleveransomradefortjanstsvar/v0\" xmlns:ns38=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tatort/v2\" xmlns:ns37=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/leveransomrade/v7\" xmlns:ns36=\"http://arbetsformedlingen.se/tjansteleverantor/request/listaleveransomradefortjanstanrop/v0\" xmlns:ns35=\"http://arbetsformedlingen.se/tjansteleverantor/response/hamtatjanstsvar/v17\" xmlns:ns34=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/status/v8\" xmlns:ns33=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tjanstekategori/v17\" xmlns:ns32=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/sprakstod/v15\" xmlns:ns31=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/omfattningsbegransning/v17\" xmlns:ns30=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/ersattningsomfattning/v13\" xmlns:ns29=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/ersattningomfattningstyp/v10\" xmlns:ns28=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tolkniva/v15\" xmlns:ns27=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tolktaxa/v17\" xmlns:ns26=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/modulprisenhet/v14\" xmlns:ns25=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/ersattningstypkod/v16\" xmlns:ns24=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/miaprisdefinitiontyp/v17\" xmlns:ns23=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/artikeltyp/v17\" xmlns:ns22=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/artikeltaxa/v17\" xmlns:ns21=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/omfattningskategori/v13\" xmlns:ns20=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/omfattningstyp/v9\" xmlns:ns19=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/omfattningsregel/v9\" xmlns:ns18=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/enhetstyp/v9\" xmlns:ns17=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/periodtyp/v9\" xmlns:ns16=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/omfattningsdefinition/v13\" xmlns:ns15=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/mia/v17\" xmlns:ns14=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/sparmiadefinitioner/v17\" xmlns:ns13=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/spar/v17\" xmlns:ns12=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/momssats/v0\" xmlns:ns11=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tidsenhet/v2\" xmlns:ns10=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/betalningsmodell/v16\" xmlns:ns9=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/tjanst/v17\" xmlns:ns8=\"http://arbetsformedlingen.se/tjansteleverantor/request/hamtatjanstanrop/v6\" xmlns:ns7=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/felmeddelande/v7\" xmlns:ns6=\"http://arbetsformedlingen.se/tjansteleverantor/undantag/verksamhetsfelmeddelande/v0\" xmlns:ns5=\"http://arbetsformedlingen.se/tjansteleverantor/undantag/systemfelmeddelande/v0\" xmlns:ns4=\"http://arbetsformedlingen.se/datatyp/gemensam/felbeskrivning/v0\" xmlns:ns3=\"http://arbetsformedlingen.se/tjansteleverantor/response/listauppfoljningskategorisvar/v0\" xmlns:ns2=\"http://arbetsformedlingen.se/datatyp/tjansteleverantor/uppfoljningskategori/v0\">\n  <ns146:tjanstekategoriLista>\n    <ns33:tjanstekategoriId>1</ns33:tjanstekategoriId>\n    <ns33:beskrivning>Utbildande tjänst</ns33:beskrivning>\n    <ns33:kod>TK01</ns33:kod>\n    <ns33:forberedandeInsats>false</ns33:forberedandeInsats>\n    <ns33:antalStangningsdagar>10</ns33:antalStangningsdagar>\n    <ns33:arStangning>false</ns33:arStangning>\n  </ns146:tjanstekategoriLista>\n  <ns146:tjanstekategoriLista>\n    <ns33:tjanstekategoriId>2</ns33:tjanstekategoriId>\n    <ns33:beskrivning>Utredande tjänst</ns33:beskrivning>\n    <ns33:kod>TK02</ns33:kod>\n    <ns33:forberedandeInsats>false</ns33:forberedandeInsats>\n    <ns33:arStangning>false</ns33:arStangning>\n  </ns146:tjanstekategoriLista>\n  <ns146:tjanstekategoriLista>\n    <ns33:tjanstekategoriId>3</ns33:tjanstekategoriId>\n    <ns33:beskrivning>Coachande tjänst</ns33:beskrivning>\n    <ns33:kod>TK03</ns33:kod>\n    <ns33:forberedandeInsats>false</ns33:forberedandeInsats>\n    <ns33:arStangning>false</ns33:arStangning>\n  </ns146:tjanstekategoriLista>\n  <ns146:tjanstekategoriLista>\n    <ns33:tjanstekategoriId>4</ns33:tjanstekategoriId>\n    <ns33:beskrivning>Lotsande tjänst</ns33:beskrivning>\n    <ns33:kod>TK04</ns33:kod>\n    <ns33:forberedandeInsats>false</ns33:forberedandeInsats>\n    <ns33:arStangning>false</ns33:arStangning>\n  </ns146:tjanstekategoriLista>\n  <ns146:tjanstekategoriLista>\n    <ns33:tjanstekategoriId>5</ns33:tjanstekategoriId>\n    <ns33:beskrivning>Stödjande tjänst</ns33:beskrivning>\n    <ns33:kod>TK05</ns33:kod>\n    <ns33:forberedandeInsats>false</ns33:forberedandeInsats>\n    <ns33:arStangning>false</ns33:arStangning>\n  </ns146:tjanstekategoriLista>\n  <ns146:tjanstekategoriLista>\n    <ns33:tjanstekategoriId>6</ns33:tjanstekategoriId>\n    <ns33:beskrivning>EKA-tjänster</ns33:beskrivning>\n    <ns33:kod>TK06</ns33:kod>\n    <ns33:forberedandeInsats>false</ns33:forberedandeInsats>\n    <ns33:arStangning>false</ns33:arStangning>\n  </ns146:tjanstekategoriLista>\n  <ns146:tjanstekategoriLista>\n    <ns33:tjanstekategoriId>7</ns33:tjanstekategoriId>\n    <ns33:beskrivning>Förberedande tjänst</ns33:beskrivning>\n    <ns33:kod>TK07</ns33:kod>\n    <ns33:forberedandeInsats>true</ns33:forberedandeInsats>\n    <ns33:arStangning>false</ns33:arStangning>\n  </ns146:tjanstekategoriLista>\n  <ns146:tjanstekategoriLista>\n    <ns33:tjanstekategoriId>8</ns33:tjanstekategoriId>\n    <ns33:beskrivning>Rapporterande</ns33:beskrivning>\n    <ns33:kod>TK08</ns33:kod>\n    <ns33:forberedandeInsats>false</ns33:forberedandeInsats>\n    <ns33:arStangning>false</ns33:arStangning>\n  </ns146:tjanstekategoriLista>\n  <ns146:tjanstekategoriLista>\n    <ns33:tjanstekategoriId>9</ns33:tjanstekategoriId>\n    <ns33:beskrivning>Resurs</ns33:beskrivning>\n    <ns33:kod>TK09</ns33:kod>\n    <ns33:forberedandeInsats>false</ns33:forberedandeInsats>\n    <ns33:arStangning>false</ns33:arStangning>\n  </ns146:tjanstekategoriLista>\n  <ns146:tjanstekategoriLista>\n    <ns33:tjanstekategoriId>10</ns33:tjanstekategoriId>\n    <ns33:beskrivning>Validerande tjänst</ns33:beskrivning>\n    <ns33:kod>TK10</ns33:kod>\n    <ns33:forberedandeInsats>false</ns33:forberedandeInsats>\n    <ns33:antalStangningsdagar>50</ns33:antalStangningsdagar>\n    <ns33:arStangning>true</ns33:arStangning>\n  </ns146:tjanstekategoriLista>\n</ns146:ListaTjanstekategoriSvarsmeddelande>"""
