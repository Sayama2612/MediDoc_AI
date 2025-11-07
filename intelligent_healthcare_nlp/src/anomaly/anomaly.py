from typing import Dict, List

# Very small rule-based anomaly checker for prescriptions
COMMON_DRUG_MAX_DOSE = {
	'paracetamol': 4000,  # mg per day
	'ibuprofen': 3200,
}


def check_prescription_dosage(meds: List[Dict]) -> List[str]:
	"""meds: list of dicts like {'name': 'paracetamol', 'dose_mg_per_day': 500}  - return list of anomaly messages"""
	alerts = []
	for m in meds:
		name = m.get('name', '').lower()
		dose = m.get('dose_mg_per_day')
		if name in COMMON_DRUG_MAX_DOSE and dose is not None:
			if dose > COMMON_DRUG_MAX_DOSE[name]:
				alerts.append(
					f'Dose for {name} is {dose}mg/day which exceeds recommended {COMMON_DRUG_MAX_DOSE[name]}mg/day'
				)
	return alerts


# Placeholder for ML-based anomaly detection (e.g., IsolationForest). Implement training later.
def ml_anomaly_stub(features):
	"""Return empty anomalies: replace with IsolationForest or Autoencoder approach."""
	return []