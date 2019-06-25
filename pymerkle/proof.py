"""
Provides the main class for `proof` objects and related functionalities
"""
import uuid
import time
import json
from .serializers import ProofSerializer
from .utils import stringify_path

NONE = '[None]'

# -------------------------------- Main class --------------------------------


class Proof(object):
    """Base class for the ``proof`` object

    Basic purpose of this class is to organize the provided proof data in a nicely formatted dictionary,
    so that they can be handled by the ``validations`` module.

    :param generation:  Should be ``'SUCCESS'`` or ``'FAILURE'`` plus explanation message, according to whether
                        or not a proof path could indeed be generated by the provider Merkle-tree
    :type generation:   str
    :param provider:    uuid of the provider Merkle-tree
    :type provider:     str
    :param hash_type:   Hash type of the provider Merkle-tree
    :type hash_type:    str
    :param security:    Security mode of the provider Merkle-tree
    :type security:     bool
    :param encoding:    Encoding type of the provider Merkle-tree
    :type encoding:     str
    :param proof_index: Path index where the validation procedure should start from
    :type proof_index:  int
    :param proof_path:  Path of signed hashes
    :type proof_path:   list of (+1/-1, bytes)

    .. note:: Required Merkle-tree parameters (``hash_type``, ``security`` and ``encoding``) are necessary for
              proof validation (cf. the ``pymerkle.validations`` module)

    Instead of providing the above arguments corresponding to `*args`, a ``proof`` object may also be constructed
    in the following ways by employing `**kwargs` in order to load the JSON string of a given proof ``p``:

    >>> from pymerkle.proof import proof
    >>> q = proof(from_json=p.JSONstring())
    >>> r = proof(from_dict=json.loads(p.JSONstring()))

    .. note:: Constructing proofs in the above ways is a genuine *replication*, since the constructed
              proofs ``q`` and ``r`` have the same *uuid* and *timestamps* as ``p``

    :ivar header:                 (*dict*) Contains the keys *uuid*, *generation*, *timestamp*, *creation_moment*,
                                  *provider*, *hash_type*, *encoding*, *security* and *status* (see below)
    :ivar header.uuid:            (*str*) uuid of the proof (time-based)
    :ivar header.generation:      (*bool*) ``True`` or ``False`` according to whether or not a proof path could
                                  indeed be generated by the provider Merkle-tree
    :ivar header.timestamp:       (*str*) Creation moment (msecs) from the start of time
    :ivar header.creation_moment: (*str*) Creation moment in human readable form
    :ivar header.provider:        (*str*) uuid of the provider Merkle-tree
    :ivar header.hash_type:       (*str*) Hash type of the provider Merkle-tree
    :ivar header.encoding:        (*str*) Encoding type of the provider Merkle-tree
    :ivar header.security:        (*bool*) Security mode of the provider Merkle-tree
    :ivar header.status:          (*bool*) ``True`` resp. ``False`` if the proof was found to be *valid*, resp. *invalid*
                                  after the last validation. If no validation has yet been performed, then it
                                  is ``None``.
    :ivar body:                   (*dict*) Contains the keys *proof_index*, *proof_path* (see below)
    :ivar body.proof_index:       (*int*) See the homonymous argument of the constructor
    :ivar body.proof_path:        (*list of (+1/-1, bytes)*) See the homonymous argument of the constructor
    """

    def __init__(self, *args, **kwargs):
        if args:                                                                # Assuming positional arguments by default
            self.header = {
                'uuid': str(uuid.uuid1()),                                      # Time based proof idW
                'timestamp': int(time.time()),
                'creation_moment': time.ctime(),
                'generation': args[4] is not None and args[5] is not None,
                'provider': args[0],
                'hash_type': args[1],
                'encoding': args[2],
                'security': args[3],
                'status': None                                                  # Will change to True or False after validation
            }

            self.body = {
                'proof_index': args[4],
                'proof_path': args[5]
            }
        else:
            if kwargs.get('from_dict'):                                         # Importing proof from dict
                self.header = kwargs.get('from_dict')['header']

                _body = kwargs.get('from_dict')['body']
                self.body = {
                    'proof_index': _body['proof_index'],
                    'proof_path': None if _body['proof_path'] == [] else tuple(tuple(pair) for pair in _body['proof_path'])
                }
            elif kwargs.get('from_json'):                                       # Importing proof from JSON text
                proof_dict = json.loads(kwargs.get('from_json'))

                self.header = proof_dict['header']

                _body = proof_dict['body']
                self.body = {
                    'proof_index': _body['proof_index'],
                    'proof_path': None if _body['proof_path'] == [] else tuple(tuple(pair) for pair in _body['proof_path'])
                }
            else:                                                               # Standard creation of a proof
                self.header = {
                    'uuid': str(uuid.uuid1()),                                  # Time based proof idW
                    'timestamp': int(time.time()),
                    'creation_moment': time.ctime(),
                    'generation': kwargs.get('proof_index') is not None and kwargs.get('proof_path') is not None,
                    'provider': kwargs.get('provider'),
                    'hash_type': kwargs.get('hash_type'),
                    'encoding': kwargs.get('encoding'),
                    'security': kwargs.get('security'),
                    'status': None                                              # Will change to True or False after validation
                }

                self.body = {
                    'proof_index': kwargs.get("proof_index"),
                    'proof_path': kwargs.get("proof_path")
                }

    def __repr__(self):
        """Overrides the default implementation.

        Sole purpose of this function is to easy print info about a proof by just invoking it at console.

        .. warning:: Contrary to convention, the output of this implementation is *not* insertible to the ``eval`` function
        """

        return '\n    ----------------------------------- PROOF ------------------------------------\
                \n\
                \n    uuid        : {uuid}\
                \n\
                \n    generation  : {generation}\
                \n    timestamp   : {timestamp} ({creation_moment})\
                \n    provider    : {provider}\
                \n\
                \n    hash-type   : {hash_type}\
                \n    encoding    : {encoding}\
                \n    security    : {security}\
                \n\
                \n    proof-index : {proof_index}\
                \n    proof-path  :\
                \n    {proof_path}\
                \n\
                \n    status      : {status}\
                \n\
                \n    -------------------------------- END OF PROOF --------------------------------\
                \n'.format(
            uuid=self.header['uuid'],
            generation='SUCCESS' if self.header['generation'] else 'FAILURE',
            timestamp=self.header['timestamp'],
            creation_moment=self.header['creation_moment'],
            provider=self.header['provider'],
            hash_type=self.header['hash_type'].upper().replace('_', '-'),
            encoding=self.header['encoding'].upper().replace('_', '-'),
            security='ACTIVATED' if self.header['security'] else 'DEACTIVATED',
            proof_index=self.body['proof_index'] if self.body['proof_index'] is not None else NONE,
            proof_path=stringify_path(self.body['proof_path'], self.header['encoding']) if self.body['proof_path'] is not None else '',
            status='UNVALIDATED' if self.header['status'] is None else 'VALID' if self.header['status'] is True else 'NON VALID')

# ------------------------------- Serialization --------------------------

    def serialize(self):
        """ Returns a JSON entity with the proof's current characteristics as key-value pairs

        :rtype: dict
        """
        return ProofSerializer().default(self)

    def JSONstring(self):
        """Returns a nicely stringified version of the proof's JSON serialized form

        .. note:: The output of this function is to be passed into the ``print`` function

        :rtype: str
        """
        return json.dumps(
            self,
            cls=ProofSerializer,
            sort_keys=True,
            indent=4)
