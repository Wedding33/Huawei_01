## NOTE: ADVANCED COMPONENTS FOR ALGORITHMS: PHASEPROB
class PhaseProb:
    @classmethod
    def get_prob(cls, event_count):
        pass
    def __init__(self, idx, num_tags, ds, ws, rs):
        self.id = idx
        self.num_tags = num_tags
        self.event_count = {
            'delete': [0] + list(ds),
            'write': [0] + list(ws),
            'read': [0] + list(rs),
        }   # NOTE: tag starts from 1

    def update_prob(self, operation, prob):
        pass