from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, SubmitField
from models import TypeOfCommittee
from wtforms.validators import DataRequired


def enum_field_options(enum):
    """Produce WTForm Field instance configuration options for an Enum

    Returns a dictionary with 'choices' and 'coerce' keys, use this as
    **enum_fields_options(EnumClass) when constructing a field:

    enum_selection = SelectField("Enum Selection", **enum_field_options(EnumClass))

    Labels are produced from str(enum_instance.value) or
    str(eum_instance), value strings with str(enum_instance).

    https://stackoverflow.com/a/51858425/14134362

    """
    assert not {'__str__', '__html__'}.isdisjoint(vars(enum)), (
        "The {!r} enum class does not implement __str__ and __html__ methods")

    def coerce(name):
        if isinstance(name, enum):
            # already coerced to instance of this enum
            return name
        try:
            return enum[name]
        except KeyError:
            raise ValueError(name)

    return {'choices': [(v.name, v) for v in enum], 'coerce': coerce}


class TypeOfCommitteeForm(FlaskForm):
    level = SelectField('Level', **enum_field_options(TypeOfCommittee.Level))
    language = SelectField('Language', **enum_field_options(TypeOfCommittee.Language))
    is_advanced = BooleanField('Advanced Committee?')
    has_important_assignments = BooleanField('Will have important assignments?')
    is_remote = BooleanField('Online Committee?')
    submit = SubmitField()

