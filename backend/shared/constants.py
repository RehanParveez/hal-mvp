PUNJAB_DIVISIONS = [
  {'division': 'Bahawalpur', 'districts': ['Bahawalnagar', 'Bahawalpur', 'Rahim Yar Khan']},
  {'division': 'Dera Ghazi Khan', 'districts': ['Dera Ghazi Khan', 'Kot Addu', 'Layyah', 'Muzaffargarh', 'Rajanpur', 'Taunsa']},
  {'division': 'Faisalabad', 'districts': ['Chiniot', 'Faisalabad', 'Jhang', 'Toba Tek Singh']},
  {'division': 'Gujranwala', 'districts': ['Gujranwala', 'Narowal', 'Sialkot']},
  {'division': 'Gujrat', 'districts': ['Gujrat', 'Hafizabad', 'Mandi Bahauddin', 'Wazirabad']},
  {'division': 'Lahore', 'districts': ['Lahore', 'Nankana Sahib', 'Kasur', 'Sheikhupura']},
  {'division': 'Multan', 'districts': ['Khanewal', 'Lodhran', 'Multan', 'Vehari']},
  {'division': 'Rawalpindi', 'districts': ['Attock', 'Chakwal', 'Jhelum', 'Murree', 'Rawalpindi', 'Talagang']},
  {'division': 'Sahiwal', 'districts': ['Okara', 'Pakpattan', 'Sahiwal']},
  {'division': 'Sargodha', 'districts': ['Bhakkar', 'Khushab', 'Mianwali', 'Sargodha']},
]

PUNJAB_DISTRICTS = [d for division in PUNJAB_DIVISIONS for d in division['districts']]

PILOT_DISTRICTS = ['Bahawalpur', 'Bahawalnagar', 'Rahim Yar Khan', 'Multan', 'Lahore', 'Faisalabad']