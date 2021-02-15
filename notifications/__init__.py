FGASES_EU = 'EU_TYPE'
AMBIGUOUS_TYPE = 'AMBIGUOUS_TYPE'
FGASES_NONEU = 'NONEU_TYPE'

FGASES_EU_GROUP_CODE = 'f-gases-eu'
FGASES_NONEU_GROUP_CODE = 'f-gases-noneu'
ODS_GROUP_CODE = 'ods'
ECR_GROUP_CODES = [ODS_GROUP_CODE, FGASES_EU_GROUP_CODE, FGASES_NONEU_GROUP_CODE]

CARS_GROUP_CODE = 'cars'
VANS_GROUP_CODE = 'vans'
BDR_GROUP_CODES = [CARS_GROUP_CODE, VANS_GROUP_CODE]

ACCEPTED_PARAMS = {
    'EXTERNAL_ID': 'company.external_id',
    'COUNTRY': 'company.country',
    'COMPANY': 'company.name',
    'CONTACT': 'person.name',
    'VAT': 'company.vat',
    'CLOSING_DATE': 'emailtemplate.stage.cycle.closing_date.strftime("%d %B %Y")',
    'OR_NAME': 'company.representative_name',
    'OR_VAT': 'company.representative_vat',
    'OR_COUNTRY': 'company.representative_country_name',
}
