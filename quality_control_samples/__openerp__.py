# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Advanced Open Source Consulting
#    Copyright (C) 2011 - 2013 Avanzosc <http://www.avanzosc.com>
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
{
    "name": "Quality Control Samples",
    "version": "1.0",
    "depends": [
        "stock",
        "mrp",
        "product",
        "quality_control",
    ],
    "author": "OdooMRP team",
    "category": "Custom Modules",
    "description": """
Se propone realizar una extensión del módulo de calidad que incluya la
siguiente funcionalidad:
    1. Adaptar campos y relaciones en el módulo standar para que sea lo más
    similar posible al formato de test enviado por Nafsa (doc Plantilla
    inspección producto nucleo móvil). En este documento, se muestra por
    ejemplo el número de unidades de muestreo, en función del producto y la
    cantidad de unidades → Nº PIEZAS INSPECCIONAR: 1-100 5,  101-500 10,
    501-1.000 15, 1.001-9.999 25, 10.000-40.000 50, lo cual nos define el
    número de tests a realizar en una recepción u orden de fabricación en
    función de las unidades recepcionadas o fabricadas.
    Se propone incluir nueva tabla muestreos en ficha producto si los rangos
    van por producto, en la categoría, si van por categoría o en una nueva
    tabla “muestreo” totalmente independiente, si los rangos son siempre los
    mismos para todos los productos. (Aclarar duda con Nafsa)

    2. Cada test irá linkado a una línea de albarán(por tanto un albarán y un
    producto concreto). Una línea podrá tener asociados varios test (según las
    muestras que sea necesario hacer) Se definirá un enlace en albaranes que
    nos permita acceder directamente a todos sus tests asociados. Un test
    corresponderá a 1 única muestra. Así, una recepción o fabricación de 50
    piezas tendrá relacionados 5 tests, con un OK, NOK independiente en cada
    uno.
    Permitir acceso al test directamente desde la línea de albarán, sin tener
    que ir a menú y facilitando la operativa del usuario de calidad.

    3. Mejorar las búsquedas de menú de tests, permitiendo buscar por número de
    albarán, OF, o producto, en el listado de tests.

    4. Crear un automatismo donde al procesar las líneas de albaranes de
    entrada contra la ubicación de calidad, automáticamente sean creados los
    tests necesarios por cada línea, sin que el operario de calidad tenga que
    crearlos manualmente. A la hora de crear el test para cada línea, se
    buscará la plantilla correspondiente para el producto, y se utilizarán los
    datos de esa plantilla para dar de alta el test. Si no existe plantilla
    para producto, se buscará plantilla para la categoría del producto, si
    existe se usará esa, y si no existe plantilla ni para producto, ni para
    categoría, se dará de alta solamente la cabecera del test. Esto no solo se
    hará con movimientos de albaranes de entrada, sino que también con el
    movimiento de salida de una OF.

    5. Incluir en el movimiento los siguientes indicadores del estado de los
    test: núm test creados, num test realizados, Num test ok, Num test Nok →
    De esta forma el usuario de calidad, sabrá directamente en la línea de
    albarán o de fabricación, cuántos tests le quedan por realizar para
    terminar.
    También se podrán tomar decisiones del tipo: Si tras realizado el muestreo
    sale una pieza defectuosa, ampliar el muestreo a 5 piezas más. En caso de
    encontrar otra defectuosa, rechazar el lote.

    6. Se propone, además, incluir un botón en la línea de albarán que cree
    automáticamente los 5 test adicionales para dicha línea. Rechazar el lote,
    implicaría crear una incidencia/no conformidad en el albarán y realizar su
    devolución total o parcial.

    7. Se propone además, poder asociar plantillas de test diferentes a
    productos concretos y o a categorías de productos concretos, de forma
    directa y no con el campo genérico de relación para facilitar búsquedas y
    enlaces desde distintos puntos de la aplicación.

Enfoque técnico:
    Relacionar un movimiento y por tanto su producto con uno o varios tests →
    relación one2many movimientos a test. Relación many2one test - movimiento,
    adicionalmente, related a producto del movimiento , a albarán(si está
    informado) y/o related a OF (si está informado). Independientemente si el
    movimiento está dentro de un albarán de entrada, salida, interno o
    fabricación incluirá el link a sus tests de calidad.
    Crear nueva tabla “rangos muestras”, relacionado a producto, categoría o
    independiente según se defina.
    Nuevo procedimiento “crear tests” al procesar albarán de proveedor a
    calidad.
    Incluir en la línea de albarán un botón “crear tests”
    Incluir en el movimiento los siguientes indicadores
        Núm test creados: Suma número total de tests relacionados con el
        movimiento
        Num test realizados: Suma Num test ok + Num test Nok
        Num test ok: Suma num test ok
        Num test Nok: Suma num test Nok
    Incluir en Plantilla de test y en test many2one a producto para limitar su
    aplicación a un producto concreto.
    Incluir en Plantilla de test y en test many2one a categorías de producto
    para limitar su aplicación a categorías de productos concretos.
    Incluir filtros y agrupaciones de búsqueda en tests por categoría de
    productos, productos, albarán, of... etc.
    """,
    'data': [
        'security/ir.model.access.csv',
        'data/quality_control_data.xml',
        'wizard/qc_test_wizard_view.xml',
        'views/mrp_production_view.xml',
        'views/stock_view.xml',
        'views/qc_test_view.xml',
        'views/sample_rank_view.xml',
    ],
    'installable': True,
}
