from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema

from trial_app import app

db = SQLAlchemy(app)

# ------------------ MODELS ------------------


class DimAgency(db.Model):
    active_producers = db.Column('activeProducers', db.Integer)
    agency_app_year = db.Column('agencyAppointmentYear', db.Integer)
    comissions_end_year = db.Column('comissionsEndYear', db.Integer)
    comissions_start_year = db.Column('comissionsStartYear', db.Integer)
    id = db.Column(db.String, primary_key=True)
    max_age = db.Column('maxAge', db.Integer)
    min_age = db.Column('minAge', db.Integer)
    vendor = db.Column(db.String(250))
    # facts = db.relationship('Facts', backref='agency', lazy=True)


class DimDate(db.Model):
    id = db.Column(db.String, primary_key=True)
    # facts = db.relationship('Facts', backref='date', lazy=True)


class DimProduct(db.Model):
    id = db.Column(db.String(25), primary_key=True)
    line = db.Column(db.String(7))
    # facts = db.relationship('Facts', backref='line', lazy=True)


class DimRiskState(db.Model):
    id = db.Column(db.String(7), primary_key=True)
    # facts = db.relationship('Facts', backref='risk', lazy=True)


class Facts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    retention_policy_quantity = db.Column(
                                'retentionPolicyQuantity', db.String)
    policy_inforce_quantity = db.Column(
                                'policyInforceQuantity', db.Integer)
    prev_policy_inforce_quantity = db.Column(
                                'prevPolicyInforceQuantity', db.Integer)
    new_business_in_written_premium = db.Column(
                                'newBusinessInWrittenPremium', db.Float)
    total_written_premium = db.Column('totalWrittenPremium', db.Float)
    earned_premium = db.Column('earnedPremium', db.Float)
    incurred_losses = db.Column('incurredLosses', db.Float)
    retention_ratio = db.Column('retentionRatio', db.Float)
    loss_ratio = db.Column('lossRatio', db.Float)
    loss_ratio_3_year = db.Column('lossRatio3Year', db.Float)
    growth_rate_3_years = db.Column('growthRate3Years', db.Float)
    bound_quotes = db.Column('boundQuotes', db.Integer)
    total_quotes = db.Column('totalQuotes', db.Integer)
    date_id = db.Column('dateId', db.String, db.ForeignKey('dim_date.id'),
                        nullable=False)
    agency_id = db.Column('agencyId', db.String,
                          db.ForeignKey('dim_agency.id'), nullable=False)
    risk_id = db.Column('riskStateId', db.String,
                        db.ForeignKey('dim_risk_state.id'), nullable=False)
    product_id = db.Column('productId', db.String, db.ForeignKey(
                           'dim_product.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('dateId', 'agencyId', 'riskStateId',
                                          'productId', name='dims_keys'), )

# ------------------ SCHEMAS ------------------


class FactsSchema(Schema):
    class Meta:
        fields = ('retention_policy_quantity', 'policy_inforce_quantity',
                  'prev_policy_inforce_quantity',
                  'new_business_in_written_premium', 'total_written_premium',
                  'earned_premium', 'incurred_losses', 'retention_ratio',
                  'loss_ratio', 'loss_ratio_3_year', 'growth_rate_3_years',
                  'bound_quotes', 'total_quotes', 'date_id', 'agency_id',
                  'risk_id', 'product_id')
        exclude = ('id',)


facts_schema = FactsSchema(many=True)
