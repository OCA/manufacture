This module provides an empty general settings section for the repair
configuration.

This is a technical module and it doesn't provide any new functionality.
Extend this module to add general settings related to the repair app.

When extending the general settings view, here is an example of how the code
would look like:

.. code:: xml

    <record id="res_config_settings_view_form" model="ir.ui.view">
        <field name="model">res.config.settings</field>
        <field name="inherit_id" ref="base_repair_config.res_config_settings_view_form"/>
        <field name="arch" type="xml">
            <xpath expr="//div[@id='configure_repair']" position="after">
                <div class="col-xs-12 col-md-6 o_setting_box">
                    <div class="o_setting_right_pane">
                        <label for="new_field_name"/>
                        <span class="fa fa-lg fa-building-o" title="Values set here are company-specific." groups="base.group_multi_company"/>
                        <div class="row">
                            <div class="text-muted col-md-8">
                                Set some configuration data for this field ...
                            </div>
                        </div>
                        <div class="content-group">
                            <div class="mt16">
                                <field name="new_field_name" class="o_light_label"/>
                            </div>
                        </div>
                    </div>
                </div>
            </xpath>
        </field>
    </record>
