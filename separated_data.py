class separated_data_buffer:
    def __init__(self):
        self.data = {
            'vocals': [],
            'drums': [],
            'bass': [],
            'other': []
        }
        self.samples_from_beginning = 0
        self.read_samples = 0
        self.first_batch_arrived = False

    def get_samples(self, samples: int, starting_sample: int):
        print("starting sample: " + str(starting_sample))
        starting_point = starting_sample - self.samples_from_beginning
        print("starting point: " + str(starting_point))
        end_point = starting_point + samples
        print("end point: " + str(end_point))
        self.read_samples = end_point
        v = self.data['vocals'][starting_point:end_point]
        b = self.data['bass'][starting_point:end_point]
        d = self.data['drums'][starting_point:end_point]
        o = self.data['other'][starting_point:end_point]
        for i in range(len(v)):
            v[i] = int((v[i][0] + v[i][1]) / 2)
            b[i] = int((b[i][0] + b[i][1]) / 2)
            d[i] = int((d[i][0] + d[i][1]) / 2)
            o[i] = int((o[i][0] + o[i][1]) / 2)
        return [v, b, d, o]

    def clear_used_data(self):
        self.samples_from_beginning += self.read_samples
        self.data['vocals'] = self.data['vocals'][self.read_samples:]
        self.data['drums'] = self.data['drums'][self.read_samples:]
        self.data['bass'] = self.data['bass'][self.read_samples:]
        self.data['other'] = self.data['other'][self.read_samples:]

    def put(self, prediction):
        for i in range(len(prediction['vocals'])):
            self.data['vocals'].append(prediction['vocals'][i])
            self.data['bass'].append(prediction['bass'][i])
            self.data['drums'].append(prediction['drums'][i])
            self.data['other'].append(prediction['other'][i])
        if not self.first_batch_arrived:
            self.first_batch_arrived = True
