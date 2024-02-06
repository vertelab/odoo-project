from odoo import models, api, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    it_asset_ids = fields.One2many('it.asset', 'partner_id', string="IT Assets")

    primary_ethernet_connection = fields.Selection([
        ('Bredband Telia 10mbit', 'Fiber Telia 10mbit'),
        ('Fiber Telia 100mbit', 'Fiber Telia 100mbit'),
        ('Bredband Telia 100mbit', 'Fiber Telia 1000mbit'),
        ('4G Telia failover', 'Fiber GlobalConnect 100mbit'),
        ('Bredband Internetport 100mbit', 'Fiber Internetport 100mbit'),
        ('ADSL Telia 4/24mbit', 'ADSL Telia 4/24mbit'),
        ('Fiber Fibia 100mbit', 'Fiber Fibia 100mbit'),
        ('Fiber Internetport 10mbit', 'Fiber Internetport 10mbit'),
        ('Fiber Nordsys 100mbit', 'Fiber Nordnet 100mbit'),
        ('Saknar Primär Uppkoppling', 'Saknar Primär Uppkoppling'),
        ('Fiber Bredband2', 'Fiber Bredband2 100mbit'),
        ('4G Telia Mobilt', '4G Telia Mobilt'),
        ('Fiber Bahnhof 100mbit', 'Fiber Bahnhof 100mbit'),
        ('Fiber Arwidsro 100mbit', 'Fiber Arwidsro 100mbit'),
        ('Gävle Energi', 'Fiber Gävle Energi 10mbit'),
        ('Fiber Gibon Västervik 100mbit', 'Fiber Gibon Västervik 100mbit'),
    ], string="Primary Ethernet Connection")

    secondary_ethernet_connection = fields.Selection([
        ('4G Telia Failover', '4G Telia Failover'),
        ('ADSL Telia', 'ADSL Telia'),
        ('Net1 Failover ', 'Net1 Failover '),
        ('4G Telenor DK', '4G Telenor DK'),
        ('4G Telia DK', '4G Telia DK'),
    ], string="Secondary Ethernet Connection")

    wifi_ethernet_connection = fields.Selection([
        ('Wifi 6 standard', 'Wifi5/6 Standard'),
        ('Wifi3/4 Standard', 'Wifi : Sophos (old)'),
    ], string="Wifi Ethernet Connection")

    kamera_system = fields.Selection([
        ('Ethiris', 'Ethiris'),
        ('Unifi Video', 'Unifi Video'),
        ('Unifi Protect', 'Unifi Protect'),
        ('Mirasys', 'Mirasys'),
    ], string="Kamera System")

    tele_system = fields.Selection([
        ('Telefoni 3cx', 'Telefoni 3cx'),
    ], string="Tele System")

