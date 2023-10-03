/** @odoo-module **/

import { evaluateExpr } from "@web/core/py_js/py";
import { XMLParser } from "@web/core/utils/xml";
import { Field } from "@web/views/fields/field";
import { archParseBoolean } from "@web/views/utils";

export class TimelineArchParser extends XMLParser {
    parse(arch, models, modelName) {
        this.visitXML(arch, (node) => {
            switch (node.tagName) {
                case "timeline": {

                }

            }
        })
    }

}