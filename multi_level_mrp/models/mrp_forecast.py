# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import date, datetime


class MrpForecastForecast(models.Model):
    _name = 'mrp.forecast.forecast'
    
    date = fields.Date('Date')
    forecast_product_id = fields.Many2one('mrp.forecast.product', 'Product',
                                          select=True)
    name = fields.Char('Description')
    qty_forecast = fields.Float('Quantity')
    
    _order = 'forecast_product_id, date'


class MrpForecastProduct(models.Model):
    _name = 'mrp.forecast.product'

    @api.one
    @api.depends('product_id')
    def _function_name(self):
        if self.product_id:
            self.name = "[%s] %s" % (self.product_id.default_code,
                                     self.product_id.name, )

    @api.one
    @api.depends('mrp_forecast_ids')
    def _function_forecast_m0(self):
        qty = 0.00
        for fc in self.mrp_forecast_ids:
            fcmonth = (datetime.date(datetime.strptime(
                fc.date, '%Y-%m-%d')).year * 100) + \
                      datetime.date(datetime.strptime(
                          fc.date, '%Y-%m-%d')).month
            tmonth = (date.today().year * 100) + date.today().month
            if not(datetime.date(datetime.strptime(
                    fc.date, '%Y-%m-%d')) < date.today()) \
                    and fcmonth == tmonth:
                qty += fc.qty_forecast
        self.qty_forecast_m0 = qty

    @api.one
    @api.depends('mrp_forecast_ids')
    def _function_forecast_m1(self):
        qty = 0.00
        for fc in self.mrp_forecast_ids:
            fcmonth = (datetime.date(datetime.strptime(
                fc.date, '%Y-%m-%d')).year * 100) + datetime.date(
                datetime.strptime(fc.date, '%Y-%m-%d')).month
            tdyear = date.today().year
            tdmonth = date.today().month + 1
            if tdmonth > 12:
                tdmonth -= 12
                tdyear += 1
            tmonth = (tdyear * 100) + tdmonth
            if fcmonth == tmonth:
                qty += fc.qty_forecast
        self.qty_forecast_m1 = qty

    @api.one
    @api.depends('mrp_forecast_ids')
    def _function_forecast_m2(self):
        qty = 0.00
        for fc in self.mrp_forecast_ids:
            fcmonth = (datetime.date(datetime.strptime(
                fc.date, '%Y-%m-%d')).year * 100) + datetime.date(
                datetime.strptime(fc.date, '%Y-%m-%d')).month
            tdyear = date.today().year
            tdmonth = date.today().month + 2
            if tdmonth > 12:
                tdmonth -= 12
                tdyear += 1
            tmonth = (tdyear * 100) + tdmonth
            if fcmonth == tmonth:
                qty += fc.qty_forecast
        self.qty_forecast_m2 = qty

    @api.one
    @api.depends('mrp_forecast_ids')
    def _function_forecast_m3(self):
        qty = 0.00
        for fc in self.mrp_forecast_ids:
            fcmonth = (datetime.date(datetime.strptime(
                fc.date, '%Y-%m-%d')).year * 100) + datetime.date(
                datetime.strptime(fc.date, '%Y-%m-%d')).month
            tdyear = date.today().year
            tdmonth = date.today().month + 3
            if tdmonth > 12:
                tdmonth -= 12
                tdyear += 1
            tmonth = (tdyear * 100) + tdmonth
            if fcmonth == tmonth:
                qty += fc.qty_forecast
        self.qty_forecast_m3 = qty

    @api.one
    @api.depends('mrp_forecast_ids')
    def _function_forecast_m4(self):
        qty = 0.00
        for fc in self.mrp_forecast_ids:
            fcmonth = (datetime.date(datetime.strptime(
                fc.date, '%Y-%m-%d')).year * 100) + datetime.date(
                datetime.strptime(fc.date, '%Y-%m-%d')).month
            tdyear = date.today().year
            tdmonth = date.today().month + 4
            if tdmonth > 12:
                tdmonth -= 12
                tdyear += 1
            tmonth = (tdyear * 100) + tdmonth
            if fcmonth == tmonth:
                qty += fc.qty_forecast
        self.qty_forecast_m4 = qty

    @api.one
    @api.depends('mrp_forecast_ids')
    def _function_forecast_m5(self):
        qty = 0.00
        for fc in self.mrp_forecast_ids:
            fcmonth = (datetime.date(datetime.strptime(
                fc.date, '%Y-%m-%d')).year * 100) + datetime.date(
                datetime.strptime(fc.date, '%Y-%m-%d')).month
            tdyear = date.today().year
            tdmonth = date.today().month + 5
            if tdmonth > 12:
                tdmonth -= 12
                tdyear += 1
            tmonth = (tdyear * 100) + tdmonth
            if fcmonth == tmonth:
                qty += fc.qty_forecast
        self.qty_forecast_m5 = qty

    @api.one
    @api.depends('mrp_forecast_ids')
    def _function_forecast_m6(self):
        qty = 0.00
        for fc in self.mrp_forecast_ids:
            fcmonth = (datetime.date(datetime.strptime(
                fc.date, '%Y-%m-%d')).year * 100) + datetime.date(
                datetime.strptime(fc.date, '%Y-%m-%d')).month
            tdyear = date.today().year
            tdmonth = date.today().month + 6
            if tdmonth > 12:
                tdmonth -= 12
                tdyear += 1
            tmonth = (tdyear * 100) + tdmonth
            if fcmonth == tmonth:
                qty += fc.qty_forecast
        self.qty_forecast_m6 = qty

    @api.one
    @api.depends('mrp_forecast_ids')
    def _function_forecast_past(self):
        qty = 0.00
        for fc in self.mrp_forecast_ids:
            if datetime.date(
                    datetime.strptime(fc.date, '%Y-%m-%d')) < date.today():
                qty += fc.qty_forecast
        self.qty_forecast_past = qty

    @api.one
    @api.depends('mrp_forecast_ids')
    def _function_forecast_total(self):
        qty = 0.00
        for fc in self.mrp_forecast_ids:
            qty += fc.qty_forecast
        self.qty_forecast_total = qty

    mrp_forecast_ids = fields.One2many('mrp.forecast.forecast',
                                       'forecast_product_id',
                                       'Forecast')
    name = fields.Char(compute='_function_name', string='Description')
    product_id = fields.Many2one('product.product', 'Product', select=True)
    mrp_area_id = fields.Many2one('mrp.area', 'MRP Area')
    qty_forecast_m0 = fields.Float(compute='_function_forecast_m0',
                                   string='This Month Forecast')
    qty_forecast_m1 = fields.Float(compute='_function_forecast_m1',
                                   string='Month+1 Forecast')
    qty_forecast_m2 = fields.Float(compute='_function_forecast_m2',
                                   string='Month+2 Forecast')
    qty_forecast_m3 = fields.Float(compute='_function_forecast_m3',
                                   string='Month+3 Forecast')
    qty_forecast_m4 = fields.Float(compute='_function_forecast_m4',
                                   string='Month+4 Forecast')
    qty_forecast_m5 = fields.Float(compute='_function_forecast_m5',
                                   string='Month+5 Forecast')
    qty_forecast_m6 = fields.Float(compute='_function_forecast_m6',
                                   string='Month+6 Forecast')
    qty_forecast_past = fields.Float(compute='_function_forecast_past',
                                     string='Past Forecast')
    qty_forecast_total = fields.Float(compute='_function_forecast_total',
                                      string='Total Forecast')
