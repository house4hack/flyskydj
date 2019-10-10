import random
import math
import json

class BaseClassifier():
    def __init__(self, classCount, stored_dict=None):
        if stored_dict is not None:
            self.load(stored_dict)
        self.classCount = classCount
        self.evidenceCount = 0

    def load(self, stored_dict):
        pass

    def train(self, input, klass):
        pass

    def classify(self, input):
        pass

    def save(self):
        pass

class NN_Classifier(BaseClassifier):
    def __init__(self, classCount, stored_dict=None):
        self.neighbours = []
        self.classes = []
        super().__init__(classCount, stored_dict)

    def load(self, stored_dict):
        self.neighbours = stored_dict['neighbours']
        self.classes = stored_dict['classes']
        self.classCount = stored_dict['classCount']
        self.evidenceCount = len(self.classes)

    def train(self, input, klass):
        self.neighbours.append(input)
        self.classes.append(klass) 
        if(len(self.neighbours)>300):
            del(self.neighbours[0])
            del(self.classes[0])
        self.evidenceCount = len(self.classes)

    def euclideanDistance(self, instance1, instance2):
        distance = 0
        for x, _ in enumerate(instance1):
            distance += pow((instance1[x] - instance2[x]), 2)
        return math.sqrt(distance)


    def classify(self, input):
        result = [0.0] * self.classCount
        for i, nbr in enumerate(self.neighbours):
            dist = self.euclideanDistance(input, nbr)
            if dist < 0.3:
                #result.append((self.classes[i], dist))
                result[self.classes[i]] += 1.0 / self.classCount

        return result, self.classCount
        
    def save(self):
        d = {'neighbours':self.neighbours, 'classes':self.classes,'classCount':self.classCount}
        return d


class NB_Classifier(BaseClassifier):
    def __init__(self, classCount, stored_dict=None):
        self.evidence = [None for i in range(classCount)]
        #self.evidenceByClass = dict([(i,0) for in range(classCount)])
        self.evidenceCountByClass = [0] * classCount
        self.alpha = 0.8

        super().__init__(classCount, stored_dict)

    def load(self, stored_dict):
        self.evidence = stored_dict['evidence']
        self.evidenceCount = stored_dict['evidenceCount']
        self.classCount = stored_dict['classCount']
        self.evidenceCountByClass = stored_dict['evidenceCountByClass']

    def train(self, input, klass):
        ev_vec = self.evidence[klass]
        if ev_vec is None:
            ev_vec = [0.5] * len(input)
        for i,v in enumerate(input):
            ev_vec[i] = ev_vec[i] * self.alpha + (1-self.alpha) * v
        self.evidence[klass] = ev_vec
        self.evidenceCount += 1
        self.evidenceCountByClass[klass] += 1
        



    def classify(self, input):
        result = []
        total_prob = 0
        for klass, ev_vec in enumerate(self.evidence):
            prob = 1.0
            if ev_vec is not None:
                for ev, val in zip(ev_vec, input):
                    if val == 0:
                        prob *= 1-ev
                    else:
                        prob *= ev

            prob *= self.evidenceCountByClass[klass] / self.evidenceCount

            result.append(prob)
            total_prob += prob
        for i, v in enumerate(result):
            result[i] = v / total_prob

        return result, self.evidenceCount


    def save(self):
        result = {"evidence":self.evidence, "evidenceCount":self.evidenceCount,\
                 "classCount":self.classCount, "evidenceCountByClass": self.evidenceCountByClass}
        return result