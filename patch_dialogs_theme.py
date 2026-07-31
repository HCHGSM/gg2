import re

with open('pos_erp/ui/dialogs.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make dialogs theme-aware
old_card_style = 'self.card.setStyleSheet("background-color: #18181B; border: 1px solid #3F3F46; border-radius: 16px;")'
new_card_style = 'self.card.setObjectName("Card")'
content = content.replace(old_card_style, new_card_style)

old_title_style = 'title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF; background: transparent; border: none;")'
new_title_style = 'title_lbl.setProperty("cssClass", "view-title")\n        title_lbl.setStyleSheet("font-size: 20px; background: transparent; border: none;")'
content = content.replace(old_title_style, new_title_style)

old_close_style = 'close_btn.setStyleSheet("background-color: transparent; border: none; color: #A1A1AA; font-size: 16px;")'
new_close_style = 'close_btn.setStyleSheet("background-color: transparent; border: none; font-size: 18px; font-weight: bold;")'
content = content.replace(old_close_style, new_close_style)

old_lbl_style = 'lbl.setStyleSheet("color: #A1A1AA; font-weight: 600; background: transparent; border: none;")'
new_lbl_style = 'lbl.setProperty("cssClass", "card-title")\n        lbl.setStyleSheet("background: transparent; border: none;")'
content = content.replace(old_lbl_style, new_lbl_style)

# The form container should stretch properly
if "self.form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)" in content:
    content = content.replace("self.form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)", 
                              "self.form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)\n        self.form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)")

with open('pos_erp/ui/dialogs.py', 'w', encoding='utf-8') as f:
    f.write(content)
