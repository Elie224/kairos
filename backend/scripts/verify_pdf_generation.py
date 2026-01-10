"""
Script pour vérifier que les PDF sont bien générés et accessibles
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_database
from app.repositories.td_repository import TDRepository
from app.repositories.tp_repository import TPRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.module_repository import ModuleRepository
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def verify_pdfs():
    """Vérifie que les PDF sont bien générés et accessibles"""
    print("=" * 60)
    print("VÉRIFICATION DES PDF (TD, TP, EXAMENS)")
    print("=" * 60)
    
    # Récupérer tous les modules
    modules = await ModuleRepository.find_all(limit=100)
    print(f"\n📚 {len(modules)} module(s) trouvé(s)\n")
    
    total_tds = 0
    tds_with_pdf = 0
    total_tps = 0
    tps_with_pdf = 0
    total_exams = 0
    exams_with_pdf = 0
    
    for module in modules:
        module_id = module.get("id")
        module_title = module.get("title", "Sans titre")
        
        print(f"\n📖 Module: {module_title}")
        print("-" * 60)
        
        # Vérifier les TD
        tds = await TDRepository.find_by_module_id(module_id)
        for td in tds:
            total_tds += 1
            pdf_url = td.get("pdf_url")
            if pdf_url:
                tds_with_pdf += 1
                print(f"  ✅ TD: {td.get('title', 'Sans titre')} - PDF disponible")
            else:
                print(f"  ⚠️  TD: {td.get('title', 'Sans titre')} - Pas de PDF")
        
        # Vérifier les TP
        tps = await TPRepository.find_by_module_id(module_id)
        for tp in tps:
            total_tps += 1
            pdf_url = tp.get("pdf_url")
            if pdf_url:
                tps_with_pdf += 1
                print(f"  ✅ TP: {tp.get('title', 'Sans titre')} - PDF disponible")
            else:
                print(f"  ⚠️  TP: {tp.get('title', 'Sans titre')} - Pas de PDF")
        
        # Vérifier les examens
        exam = await ExamRepository.find_by_module_id(module_id)
        if exam:
            total_exams += 1
            pdf_url = exam.get("pdf_url")
            if pdf_url:
                exams_with_pdf += 1
                print(f"  ✅ Examen - PDF disponible")
            else:
                print(f"  ⚠️  Examen - Pas de PDF")
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"TD: {tds_with_pdf}/{total_tds} avec PDF ({tds_with_pdf*100//total_tds if total_tds > 0 else 0}%)")
    print(f"TP: {tps_with_pdf}/{total_tps} avec PDF ({tps_with_pdf*100//total_tps if total_tps > 0 else 0}%)")
    print(f"Examens: {exams_with_pdf}/{total_exams} avec PDF ({exams_with_pdf*100//total_exams if total_exams > 0 else 0}%)")
    print("=" * 60)
    
    # Vérifier que les fichiers PDF existent
    pdf_dir = Path("uploads/resources")
    if pdf_dir.exists():
        pdf_files = list(pdf_dir.glob("*.pdf"))
        print(f"\n📄 {len(pdf_files)} fichier(s) PDF trouvé(s) dans uploads/resources/")
    else:
        print("\n⚠️  Le dossier uploads/resources/ n'existe pas")


if __name__ == "__main__":
    asyncio.run(verify_pdfs())
