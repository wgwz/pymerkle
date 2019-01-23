from .tree import merkle_tree
from .validations import validate_proof, proof_validator

name = "pymerkle"  # Just for verifying correct installation

__version__ = "0.1.2"
__all__ = (
    'merkle_tree',
    'validate_proof',
    'proof_validator')
