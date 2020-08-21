from openerp import models, api


def get_neighbor_element(my_itr, initial=None):
    try:
        val = my_itr.next()
        if initial:
            while val != initial:
                val = my_itr.next()
            val = my_itr.next()
        return val
    except StopIteration:
        return None


class AbstractSelectionRotate(models.Model):
    _name = "abstract.selection.rotate"

    @api.multi
    def _iter_selection(self, direction):
        " Allows to update the field selection value "
        if "selection_field" not in self.env.context:
            return True
        field = self.env.context["selection_field"]
        # extract first value in each tuple as content of the selection field
        values = [elm[0] for elm in self._get_values_from_selection(field)]
        if direction == "prev":
            values = reversed(values)
        my_itr = iter(values)
        for item in self:
            initial = item[field]
            value = get_neighbor_element(my_itr, initial)
            if value is None:
                my_itr = iter(values)
                value = get_neighbor_element(my_itr)
            item.write({field: value})
        return True

    @api.multi
    def iter_selection_next(self):
        """ You can trigger this method by this xml declaration
            in your own view to iterate field selection

            <button name="iter_selection_next"
                    context="{'selection_field': 'my_selection_field'}"
                    icon="gtk-go-forward"
                    type="object"/>
        """
        self._iter_selection("next")
        return True

    @api.multi
    def iter_selection_prev(self):
        " see previous method "
        self._iter_selection("prev")
        return True

    @api.multi
    def _get_values_from_selection(self, field):
        """ Override this method
            to return your own list of tuples
            which match with field selection values or a sub part

            [('val1', 'My Val1'),
             ('val2', 'My Val2')]
        """
        return [
            (),
        ]
