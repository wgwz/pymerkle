"""
Tests proof generation methods
"""

import pytest

from pymerkle import MerkleTree
from pymerkle.hashing import SUPPORTED_ALGORITHMS

from tests.conftest import option, resolve_encodings


# Trees setup

MAX_LENGTH = 4
trees = []
for security in (True, False):
    for length in range(0, MAX_LENGTH + 1):
        for algorithm in SUPPORTED_ALGORITHMS:
            for encoding in resolve_encodings(option):
                config = {'algorithm': algorithm, 'encoding': encoding,
                          'security': security}
                tree = MerkleTree.init_from_records(
                    *['%d-th record' % _ for _ in range(length)],
                    config=config)
                trees.append(tree)


tree__wrong_challenge = []
tree_challenge = []

for tree in trees:

    tree__wrong_challenge.append(
        (
            tree,
            b'anything that has not been recorded'
        )
    )

    for i in range(tree.length):
        tree_challenge.append(
            (
                tree,
                tree.hash_data('%d-th record' % i)
            )
        )


@pytest.mark.parametrize('tree, challenge', tree__wrong_challenge)
def test_empty_generate_audit_proof(tree, challenge):
    proof = tree.generate_audit_proof(challenge)

    assert proof.__dict__ == {
        'uuid': proof.uuid,
        'timestamp': proof.timestamp,
        'created_at': proof.created_at,
        'algorithm': tree.algorithm,
        'encoding': tree.encoding,
        'security': tree.security,
        'commitment': proof.commitment,
        'offset': -1,
        'path': [],
    }


@pytest.mark.parametrize('tree, challenge', tree_challenge)
def test_non_empty_generate_audit_proof(tree, challenge):
    proof = tree.generate_audit_proof(challenge)

    assert proof.__dict__ == {
        'uuid': proof.uuid,
        'timestamp': proof.timestamp,
        'created_at': proof.created_at,
        'algorithm': tree.algorithm,
        'encoding': tree.encoding,
        'security': tree.security,
        'commitment': proof.commitment,
        'offset': proof.offset,
        'path': proof.path,
    }


# Consistency proof

trees_and_subtrees = []

for tree in trees:
    for sublength in range(1, tree.length + 1):

        trees_and_subtrees.append(
            (
                tree,
                MerkleTree.init_from_records(
                    *['%d-th record' % _ for _ in range(sublength)],
                    config=tree.get_config())
            )
        )


tree_challenge = []

for (tree, subtree) in trees_and_subtrees:

    tree_challenge.append(
        (
            tree,
            subtree.get_root_hash(),
        )
    )


@pytest.mark.parametrize('tree, challenge', tree_challenge)
def test_non_empty_generate_consistency_proof(tree, challenge):
    proof = tree.generate_consistency_proof(challenge)

    assert proof.__dict__ == {
        'uuid': proof.uuid,
        'timestamp': proof.timestamp,
        'created_at': proof.created_at,
        'algorithm': tree.algorithm,
        'encoding': tree.encoding,
        'security': tree.security,
        'commitment': proof.commitment,
        'offset': proof.offset,
        'path': proof.path,
    }


@pytest.mark.parametrize('tree, challenge', tree_challenge)
def test_empty_generate_consistency_proof_with_wrong_challenge(tree, challenge):
    proof = tree.generate_consistency_proof(challenge)

    assert proof.__dict__ == {
        'uuid': proof.uuid,
        'timestamp': proof.timestamp,
        'created_at': proof.created_at,
        'algorithm': tree.algorithm,
        'encoding': tree.encoding,
        'security': tree.security,
        'commitment': proof.commitment,
        'offset': proof.offset,
        'path': proof.path,
    }


@pytest.mark.parametrize('tree, challenge', tree_challenge)
def test_empty_generate_consistency_proof_with_wrong_challenge(tree, challenge):
    proof = tree.generate_consistency_proof(challenge)

    assert proof.__dict__ == {
        'uuid': proof.uuid,
        'timestamp': proof.timestamp,
        'created_at': proof.created_at,
        'algorithm': tree.algorithm,
        'encoding': tree.encoding,
        'security': tree.security,
        'commitment': proof.commitment,
        'offset': proof.offset,
        'path': proof.path,
    }
