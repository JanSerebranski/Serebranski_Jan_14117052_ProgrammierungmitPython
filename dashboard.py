import json
from datetime import datetime

# ---------------------------
# Entitätsklassen
# ---------------------------

class Pruefungsleistung:
    """
    Repräsentiert eine Prüfungsleistung mit Note und Versuchszähler.
    """
    def __init__(self, note: float, versuch: int):
        self.note = note
        self.versuch = versuch

    def to_dict(self):
        """
        Serialisiert die Prüfungsleistung als Dictionary.
        """
        return {"note": self.note, "versuch": self.versuch}

    @classmethod
    def from_dict(cls, data: dict):
        """
        Erzeugt eine Prüfungsleistung aus einem Dictionary.
        """
        return cls(note=data["note"], versuch=data["versuch"])


class Modul:
    """
    Repräsentiert ein Modul mit Modulnamen, ECTS-Punkten, Status und 
    möglichen Prüfungsleistungen. Zusätzlich kann eine Endnote gespeichert werden.
    """
    def __init__(self, modulName: str, ects: int, status: str, note: float = None):
        self.modulName = modulName
        self.ects = ects
        self.status = status  # z.B. "Abgeschlossen" oder "In Bearbeitung"
        self.note = note      # Endnote, falls bereits vergeben
        self.pruefungen = []  # Liste von Pruefungsleistung-Objekten

    def addPruefungsleistung(self, p: Pruefungsleistung):
        """
        Fügt eine Prüfungsleistung hinzu und aktualisiert ggf. die Endnote.
        """
        self.pruefungen.append(p)
        # Hier wird die Endnote als die Note der zuletzt hinzugefügten Prüfungsleistung gesetzt.
        self.note = p.note

    def getAktuelleNote(self):
        """
        Gibt die aktuelle Note des Moduls zurück.
        """
        return self.note

    def to_dict(self):
        """
        Serialisiert das Modul als Dictionary.
        """
        return {
            "modulName": self.modulName,
            "ects": self.ects,
            "status": self.status,
            "note": self.note,
            "pruefungen": [p.to_dict() for p in self.pruefungen]
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Erzeugt ein Modul aus einem Dictionary.
        """
        modul = cls(
            modulName=data["modulName"],
            ects=data["ects"],
            status=data["status"],
            note=data.get("note")
        )
        modul.pruefungen = [Pruefungsleistung.from_dict(p) for p in data.get("pruefungen", [])]
        return modul


class Semester:
    """
    Repräsentiert ein Semester mit einer Nummer, Start- und Enddatum sowie einer Liste von Modulen.
    """
    def __init__(self, semesterNummer: int, startDatum: str = None, endDatum: str = None):
        self.semesterNummer = semesterNummer
        self.startDatum = startDatum  # z.B. "2023-10-01"
        self.endDatum = endDatum      # z.B. "2024-03-31"
        self.module = []             # Liste von Modul-Objekten

    def addModul(self, m: Modul):
        """
        Fügt ein Modul dem Semester hinzu.
        """
        self.module.append(m)

    def removeModul(self, m: Modul):
        """
        Entfernt ein Modul aus dem Semester.
        """
        self.module.remove(m)

    def to_dict(self):
        """
        Serialisiert das Semester als Dictionary.
        """
        return {
            "semesterNummer": self.semesterNummer,
            "startDatum": self.startDatum,
            "endDatum": self.endDatum,
            "module": [m.to_dict() for m in self.module]
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Erzeugt ein Semester aus einem Dictionary.
        """
        sem = cls(
            semesterNummer=data["semesterNummer"],
            startDatum=data.get("startDatum"),
            endDatum=data.get("endDatum")
        )
        sem.module = [Modul.from_dict(m) for m in data.get("module", [])]
        return sem


class Studiengang:
    """
    Repräsentiert einen Studiengang mit Namen, der Gesamtanzahl an ECTS-Punkten 
    und einer Liste von Semestern.
    """
    def __init__(self, name: str, gesamtECTS: int):
        self.name = name
        self.gesamtECTS = gesamtECTS
        self.semester = []  # Liste von Semester-Objekten

    def addSemester(self, s: Semester):
        """
        Fügt ein Semester dem Studiengang hinzu.
        """
        self.semester.append(s)

    def getNotendurchschnitt(self) -> float:
        """
        Berechnet den Notendurchschnitt aller Module, die bereits eine Endnote besitzen.
        """
        noten = []
        for sem in self.semester:
            for mod in sem.module:
                if mod.note is not None:
                    noten.append(mod.note)
        return sum(noten) / len(noten) if noten else 0.0

    def getFortschrittECTS(self) -> int:
        """
        Berechnet die Summe der ECTS-Punkte aller abgeschlossenen Module.
        """
        earned = 0
        for sem in self.semester:
            for mod in sem.module:
                if mod.status.lower() == "abgeschlossen":
                    earned += mod.ects
        return earned

    def to_dict(self):
        """
        Serialisiert den Studiengang als Dictionary.
        """
        return {
            "name": self.name,
            "gesamtECTS": self.gesamtECTS,
            "semester": [s.to_dict() for s in self.semester]
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Erzeugt einen Studiengang aus einem Dictionary.
        """
        stg = cls(name=data["name"], gesamtECTS=data["gesamtECTS"])
        stg.semester = [Semester.from_dict(s) for s in data.get("semester", [])]
        return stg


# ---------------------------
# Service-Klassen
# ---------------------------

class DashboardService:
    """
    Service-Klasse zur Berechnung und Darstellung der Dashboard-Kennzahlen.
    """
    @staticmethod
    def berechneNotenschnitt(stg: Studiengang) -> float:
        """
        Berechnet den Notendurchschnitt des Studiengangs.
        
        :param stg: Studiengang-Objekt
        :return: Durchschnittsnote
        """
        return stg.getNotendurchschnitt()

    @staticmethod
    def berechneFortschritt(stg: Studiengang) -> int:
        """
        Berechnet die in ECTS-Punkten erreichte Studienleistung.
        
        :param stg: Studiengang-Objekt
        :return: Erreichte ECTS-Punkte
        """
        return stg.getFortschrittECTS()

    @staticmethod
    def displayDashboard(stg: Studiengang):
        """
        Zeigt alle relevanten Informationen des Dashboards an, inklusive
        aktueller Semesterdetails, Notendurchschnitt und ECTS-Fortschritt.
        
        :param stg: Studiengang-Objekt
        """
        print(f"Studiengang: {stg.name}")
        print(f"Gesamt-ECTS: {stg.gesamtECTS}")
        earned_ects = stg.getFortschrittECTS()
        progress_percentage = (earned_ects / stg.gesamtECTS * 100) if stg.gesamtECTS > 0 else 0
        print(f"Erreichte ECTS: {earned_ects} ({progress_percentage:.2f}%)")
        print(f"Notendurchschnitt: {stg.getNotendurchschnitt():.2f}")
        print("Semesterübersicht:")
        for sem in stg.semester:
            print(f"  Semester {sem.semesterNummer} (von {sem.startDatum} bis {sem.endDatum}):")
            for mod in sem.module:
                note = mod.getAktuelleNote()
                note_str = f"{note:.2f}" if note is not None else "Keine Note"
                print(f"    Modul: {mod.modulName}, ECTS: {mod.ects}, Status: {mod.status}, Note: {note_str}")


class PersistenceService:
    """
    Service-Klasse zur Speicherung und zum Laden der Studiengangsdaten im JSON-Format.
    """
    @staticmethod
    def saveData(datei: str, stg: Studiengang):
        """
        Speichert die Daten des Studiengangs in eine JSON-Datei.
        
        :param datei: Dateiname
        :param stg: Studiengang-Objekt
        """
        try:
            with open(datei, "w", encoding="utf-8") as f:
                json.dump(stg.to_dict(), f, ensure_ascii=False, indent=4)
            print(f"Daten erfolgreich in '{datei}' gespeichert.")
        except Exception as e:
            print(f"Fehler beim Speichern der Daten: {e}")

    @staticmethod
    def loadData(datei: str) -> Studiengang:
        """
        Lädt die Daten des Studiengangs aus einer JSON-Datei.
        
        :param datei: Dateiname
        :return: Studiengang-Objekt
        """
        try:
            with open(datei, "r", encoding="utf-8") as f:
                data = json.load(f)
            stg = Studiengang.from_dict(data)
            print(f"Daten erfolgreich aus '{datei}' geladen.")
            return stg
        except Exception as e:
            print(f"Fehler beim Laden der Daten: {e}")
            return None


# ---------------------------
# Hauptprogramm (CLI-Prototyp)
# ---------------------------

def main():
    """
    Hauptfunktion zur Demonstration des Dashboard-Prototyps.
    
    Es wird ein Beispiel-Studiengang erstellt, Semester und Module
    werden hinzugefügt, und es werden Dashboard-Kennzahlen (Notendurchschnitt
    und ECTS-Fortschritt) berechnet und angezeigt.
    """
    # Erstellen eines Beispiel-Studiengangs
    stg = Studiengang("Angewandte KI", 180)

    # Erstellen des 1. Semesters
    sem1 = Semester(semesterNummer=1, startDatum="2023-10-01", endDatum="2024-03-31")
    
    # Hinzufügen von Modulen zum 1. Semester
    mathe = Modul("Mathe I", 8, "Abgeschlossen", 2.3)
    # Prüfungsleistung zu Mathe hinzufügen
    mathe.addPruefungsleistung(Pruefungsleistung(2.3, 1))
    
    programmierung = Modul("Programmierung", 10, "In Bearbeitung")
    
    sem1.addModul(mathe)
    sem1.addModul(programmierung)
    stg.addSemester(sem1)

    # Erstellen des 2. Semesters
    sem2 = Semester(semesterNummer=2, startDatum="2024-04-01", endDatum="2024-09-30")
    datenbanken = Modul("Datenbanken", 6, "Abgeschlossen", 2.0)
    datenbanken.addPruefungsleistung(Pruefungsleistung(2.0, 1))
    sem2.addModul(datenbanken)
    stg.addSemester(sem2)

    # Dashboard anzeigen
    print("\n--- Dashboard ---")
    DashboardService.displayDashboard(stg)

    # Beispiel: Speichern der Daten in einer JSON-Datei
    dateiname = "studiengang.json"
    PersistenceService.saveData(dateiname, stg)

    # Laden der Daten aus der JSON-Datei und erneutes Anzeigen des Dashboards
    geladen_stg = PersistenceService.loadData(dateiname)
    if geladen_stg:
        print("\n--- Dashboard (geladene Daten) ---")
        DashboardService.displayDashboard(geladen_stg)


if __name__ == "__main__":
    main()
