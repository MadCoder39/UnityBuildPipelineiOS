from os.path import join


class Encoder:
    def __init__(self, encode_func):
        self._encode_func = encode_func

    def encode(self, conf):
        return [
            self._encode_func(key, val)
            for key, val in conf.items() if val
        ]


pair_encoder = Encoder(
    lambda k, v: f'{k} "{v}"'
)


class Appfile:
    app_id = ''
    apple_id = ''

    def to_text(self):
        lines = self._serialize_assigned()
        return '\n'.join(lines)

    def _serialize_assigned(self):
        lines = pair_encoder.encode(self._get_pairs())
        return lines

    def _get_pairs(self):
        return {
            'app_identifier': self.app_id,
            'apple_id': self.apple_id
        }

    def save(self, path, filename):
        with open(join(path, filename), 'w') as f:
            f.write(self.to_text())

