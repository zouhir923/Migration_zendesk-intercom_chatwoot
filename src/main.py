import os
import sys
from src.api.zendesk_client import ZendeskClient
from src.api.intercom_client import IntercomClient
from src.services.zendesk_service import ZendeskService
from src.services.intercom_service import IntercomService
from src.services.zendesk_clean_service import zendesk_clean_all
from src.services.intercom_clean_service import intercom_clean_all
from configs.config import validate_config


def check_setup():
    """Vérification rapide"""
    print("Vérification configuration...")
    try:
        validate_config()
        return True
    except ValueError as e:
        print(f"Erreur config: {e}")
        return False


def test_apis():
    """Test connexions"""
    zendesk_ok = intercom_ok = False
    
    try:
        zendesk_ok = ZendeskClient().test_connection()
    except:
        print("Zendesk: Erreur connexion")
    
    try:
        intercom_ok = IntercomClient().test_connection()
    except:
        print("Intercom: Erreur connexion")
    
    return zendesk_ok, intercom_ok


def run_export(zendesk=True, intercom=True):
    """Export données"""
    files = {}
    
    if zendesk:
        try:
            print("\nExport Zendesk...")
            files.update(ZendeskService().export_all())
        except Exception as e:
            print(f"Erreur export Zendesk: {e}")
    
    if intercom:
        try:
            print("\nExport Intercom...")
            files.update(IntercomService().export_all())
        except Exception as e:
            print(f"Erreur export Intercom: {e}")
    
    return files


def run_clean(zendesk=True, intercom=True):
    """Clean données"""
    files = {}
    
    if zendesk:
        try:
            print("\nClean Zendesk...")
            files.update(zendesk_clean_all())
        except Exception as e:
            print(f"Erreur clean Zendesk: {e}")
    
    if intercom:
        try:
            print("\nClean Intercom...")
            files.update(intercom_clean_all())
        except Exception as e:
            print(f"Erreur clean Intercom: {e}")
    
    return files


def main():
    """Menu principal"""
    print("MIGRATION ZENDESK & INTERCOM")
    print("1. Complet (Export + Clean)")
    print("2. Zendesk seulement")  
    print("3. Intercom seulement")
    print("4. Export seulement")
    print("5. Clean seulement")
    print("6. Test connexions")
    
    choice = input("Choix (1-6): ")
    
    if not check_setup():
        return
    
    zendesk_ok, intercom_ok = test_apis()
    
    if choice == "1":
        run_export(zendesk_ok, intercom_ok)
        run_clean(zendesk_ok, intercom_ok)
    elif choice == "2":
        if zendesk_ok:
            run_export(True, False)
            run_clean(True, False)
    elif choice == "3":
        if intercom_ok:
            run_export(False, True)
            run_clean(False, True)
    elif choice == "4":
        run_export(zendesk_ok, intercom_ok)
    elif choice == "5":
        run_clean(True, True)
    elif choice == "6":
        print(f"Zendesk: {'OK' if zendesk_ok else 'ERREUR'}")
        print(f"Intercom: {'OK' if intercom_ok else 'ERREUR'}")
    
    print("\nTerminé!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrompu")
    except Exception as e:
        print(f"Erreur: {e}")