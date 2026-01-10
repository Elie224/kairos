"""
Service pour les laboratoires virtuels interactifs
Simulations physique et chimie
"""
from typing import Dict, Any, List, Optional
from app.repositories.module_repository import ModuleRepository
import logging
import json

logger = logging.getLogger(__name__)


class LabSimulationService:
    """Service pour simulations de laboratoire"""
    
    @staticmethod
    async def get_simulation_config(
        module_id: str,
        simulation_type: str = "physics"
    ) -> Dict[str, Any]:
        """
        Récupère la configuration de simulation pour un module
        """
        try:
            module = await ModuleRepository.find_by_id(module_id)
            if not module:
                raise ValueError(f"Module {module_id} non trouvé")
            
            subject = module.get("subject")
            
            # Configuration selon le type de simulation
            if simulation_type == "physics":
                return LabSimulationService._get_physics_config(module)
            elif simulation_type == "chemistry":
                return LabSimulationService._get_chemistry_config(module)
            else:
                return LabSimulationService._get_generic_config(module)
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de config simulation: {e}", exc_info=True)
            raise
    
    @staticmethod
    def _get_physics_config(module: Dict[str, Any]) -> Dict[str, Any]:
        """Configuration pour simulation physique"""
        title = module.get("title", "")
        
        # Détecter le type de simulation selon le titre
        if "gravitation" in title.lower() or "gravité" in title.lower():
            return {
                "type": "gravity",
                "parameters": {
                    "mass1": {"min": 1, "max": 100, "default": 10, "unit": "kg"},
                    "mass2": {"min": 1, "max": 100, "default": 10, "unit": "kg"},
                    "distance": {"min": 1, "max": 1000, "default": 100, "unit": "m"},
                    "gravity_constant": {"value": 6.67430e-11, "unit": "N⋅m²/kg²"}
                },
                "visualizations": ["force_vectors", "trajectory", "field_lines"],
                "formulas": {
                    "gravitational_force": "F = G * (m1 * m2) / r²"
                }
            }
        elif "électricité" in title.lower() or "electric" in title.lower():
            return {
                "type": "electricity",
                "parameters": {
                    "voltage": {"min": 0, "max": 100, "default": 12, "unit": "V"},
                    "current": {"min": 0, "max": 10, "default": 2, "unit": "A"},
                    "resistance": {"min": 0.1, "max": 1000, "default": 6, "unit": "Ω"}
                },
                "visualizations": ["circuit_diagram", "current_flow", "voltage_graph"],
                "formulas": {
                    "ohms_law": "V = I * R",
                    "power": "P = V * I"
                }
            }
        elif "magnétisme" in title.lower() or "magnetic" in title.lower():
            return {
                "type": "magnetism",
                "parameters": {
                    "magnetic_field": {"min": 0, "max": 10, "default": 1, "unit": "T"},
                    "current": {"min": 0, "max": 10, "default": 2, "unit": "A"},
                    "distance": {"min": 0.1, "max": 10, "default": 1, "unit": "m"}
                },
                "visualizations": ["field_lines", "force_direction", "field_strength"],
                "formulas": {
                    "magnetic_force": "F = q * v * B",
                    "field_strength": "B = μ₀ * I / (2πr)"
                }
            }
        else:
            return LabSimulationService._get_generic_config(module)
    
    @staticmethod
    def _get_chemistry_config(module: Dict[str, Any]) -> Dict[str, Any]:
        """Configuration pour simulation chimie"""
        title = module.get("title", "")
        
        if "réaction" in title.lower() or "reaction" in title.lower():
            return {
                "type": "chemical_reaction",
                "parameters": {
                    "reactant1_concentration": {"min": 0.1, "max": 10, "default": 1, "unit": "mol/L"},
                    "reactant2_concentration": {"min": 0.1, "max": 10, "default": 1, "unit": "mol/L"},
                    "temperature": {"min": 0, "max": 100, "default": 25, "unit": "°C"},
                    "catalyst": {"options": ["none", "enzyme", "metal"], "default": "none"}
                },
                "visualizations": ["reaction_equation", "concentration_graph", "energy_diagram"],
                "formulas": {
                    "rate_law": "rate = k * [A]^m * [B]^n",
                    "equilibrium": "K = [products] / [reactants]"
                }
            }
        elif "atom" in title.lower() or "structure" in title.lower():
            return {
                "type": "atomic_structure",
                "parameters": {
                    "element": {"options": ["H", "He", "Li", "C", "O", "Na"], "default": "H"},
                    "energy_level": {"min": 1, "max": 7, "default": 1},
                    "electron_count": {"min": 1, "max": 118, "default": 1}
                },
                "visualizations": ["electron_shells", "orbital_shapes", "energy_levels"],
                "formulas": {
                    "energy": "E = -13.6 * Z² / n² eV"
                }
            }
        else:
            return LabSimulationService._get_generic_config(module)
    
    @staticmethod
    def _get_generic_config(module: Dict[str, Any]) -> Dict[str, Any]:
        """Configuration générique"""
        return {
            "type": "generic",
            "parameters": {
                "parameter1": {"min": 0, "max": 100, "default": 50, "unit": ""},
                "parameter2": {"min": 0, "max": 100, "default": 50, "unit": ""}
            },
            "visualizations": ["graph", "3d_view"],
            "formulas": {}
        }
    
    @staticmethod
    async def calculate_simulation(
        module_id: str,
        parameters: Dict[str, Any],
        simulation_type: str = "physics"
    ) -> Dict[str, Any]:
        """
        Calcule les résultats d'une simulation avec paramètres donnés
        """
        try:
            config = await LabSimulationService.get_simulation_config(module_id, simulation_type)
            
            # Calculs selon le type
            if config["type"] == "gravity":
                return LabSimulationService._calculate_gravity(parameters)
            elif config["type"] == "electricity":
                return LabSimulationService._calculate_electricity(parameters)
            elif config["type"] == "magnetism":
                return LabSimulationService._calculate_magnetism(parameters)
            elif config["type"] == "chemical_reaction":
                return LabSimulationService._calculate_reaction(parameters)
            else:
                return {"result": "Simulation générique", "values": parameters}
                
        except Exception as e:
            logger.error(f"Erreur lors du calcul de simulation: {e}", exc_info=True)
            raise
    
    @staticmethod
    def _calculate_gravity(params: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule la force gravitationnelle"""
        m1 = params.get("mass1", 10)
        m2 = params.get("mass2", 10)
        r = params.get("distance", 100)
        G = 6.67430e-11
        
        force = G * (m1 * m2) / (r ** 2)
        
        return {
            "force": force,
            "unit": "N",
            "formula_used": "F = G * (m1 * m2) / r²",
            "values": {
                "mass1": m1,
                "mass2": m2,
                "distance": r,
                "gravitational_constant": G
            }
        }
    
    @staticmethod
    def _calculate_electricity(params: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule les valeurs électriques"""
        voltage = params.get("voltage", 12)
        current = params.get("current", 2)
        resistance = params.get("resistance", 6)
        
        # Calculs selon la loi d'Ohm
        if voltage and current:
            calculated_resistance = voltage / current
        elif voltage and resistance:
            calculated_current = voltage / resistance
        elif current and resistance:
            calculated_voltage = current * resistance
        else:
            calculated_resistance = resistance
            calculated_current = current
            calculated_voltage = voltage
        
        power = voltage * current
        
        return {
            "voltage": calculated_voltage if 'calculated_voltage' in locals() else voltage,
            "current": calculated_current if 'calculated_current' in locals() else current,
            "resistance": calculated_resistance if 'calculated_resistance' in locals() else resistance,
            "power": power,
            "formula_used": "V = I * R, P = V * I"
        }
    
    @staticmethod
    def _calculate_magnetism(params: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule les valeurs magnétiques"""
        B = params.get("magnetic_field", 1)
        I = params.get("current", 2)
        r = params.get("distance", 1)
        mu0 = 4 * 3.14159 * 1e-7
        
        field_strength = mu0 * I / (2 * 3.14159 * r)
        
        return {
            "magnetic_field": B,
            "field_strength": field_strength,
            "current": I,
            "distance": r,
            "formula_used": "B = μ₀ * I / (2πr)"
        }
    
    @staticmethod
    def _calculate_reaction(params: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule les valeurs de réaction chimique"""
        conc1 = params.get("reactant1_concentration", 1)
        conc2 = params.get("reactant2_concentration", 1)
        temp = params.get("temperature", 25)
        
        # Calcul simplifié de taux de réaction
        rate = conc1 * conc2 * (1 + temp / 100)
        
        return {
            "reaction_rate": rate,
            "reactant1_concentration": conc1,
            "reactant2_concentration": conc2,
            "temperature": temp,
            "formula_used": "rate = k * [A] * [B] * f(T)"
        }











