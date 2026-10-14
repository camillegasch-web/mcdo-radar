#!/usr/bin/env python3
"""Tests hors réseau de la pertinence du radar ; exécutés avant collecte quotidienne."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import update_news as radar

def article(title, section, source="Média test"):
    return {
      "title":title,"section":section,"source":source,
      "date":radar.NOW.isoformat(),"url":"https://example.com/articles/"+str(len(title))+"-"+title[:8],
      "sections":[section],"channel":"Google Actualités"
    }

class EditorialTests(unittest.TestCase):
    def test_local_requires_mcdo(self):
        self.assertIsNone(radar.classify(article("Un bar de Nantes organise un forum de l'emploi","Local","Actu.fr")))
        real=radar.classify(article("McDonald’s ouvre un restaurant à Nantes et recrute des équipiers","Local","Actu.fr"))
        self.assertIsNotNone(real)
        self.assertIn("Local",real["sections"])
        self.assertIn("RH McDo",real["sections"])
    def test_concurrence_requires_brand(self):
        self.assertIsNone(radar.classify(article("Un nouveau café naturel lancé en grande distribution","Concurrence","LSA")))
        self.assertIn("Concurrence",radar.classify(article("Burger King lance une campagne de publicité","Concurrence"))["sections"])
    def test_hr_no_individual_job_ads(self):
        self.assertIsNone(radar.classify(article("Chef de rang (H/F) - CDI à Paris","Inspiration RH","L'Hôtellerie Restauration")))
        self.assertIn("Inspiration RH",radar.classify(article("Étude : le recrutement des jeunes cadres évolue","Inspiration RH"))["sections"])
    def test_campaign_is_not_generic_social_media(self):
        self.assertIsNone(radar.classify(article("Les réseaux sociaux les plus utilisés en 2026","Campagnes créatives","Blog du Modérateur")))
        self.assertIn("Campagnes créatives",radar.classify(article("Une marque dévoile sa campagne publicitaire pour Noël","Campagnes créatives"))["sections"])
    def test_sensitive_only_related_to_enseigne(self):
        self.assertIsNone(radar.classify(article("Une grève de la justice à Bordeaux","Signaux sensibles")))
        self.assertIn("Signaux sensibles",radar.classify(article("Des équipiers de McDonald's en grève","Signaux sensibles"))["sections"])
    def test_study_tags(self):
        a=radar.classify(article("Baromètre : l'attractivité du recrutement chez les jeunes salariés","Inspiration RH"))
        radar.editorial_metadata(a)
        self.assertIn("studies",a["editorial"]["tags"])
    def test_weekly_selection_diverse(self):
        entries=[]
        for kind,n in [("France",3),("Inspiration RH",4),("Campagnes créatives",4),("Concurrence",2)]:
            for i in range(n):
                a=article("McDonald's opération locale "+kind+str(i),kind,"Média numéro "+str(i)+" "+kind)
                a["editorial"]={"score":79-i}
                entries.append(a)
        picks=radar.weekly_picks(entries)
        self.assertEqual(10,len(picks["items"]))
if __name__=="__main__":
    unittest.main()
