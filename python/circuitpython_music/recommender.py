import math
import random
import classifier

UNKNOWN = -1
SLOW = 0 
FAST = 1
 
class Recommender():
    def __init__(self, classCount, final_epsilon=0.05, alt_hist_alpha=0.995, vario_hist_alpha=0.95):
        self.init_hist()
        self.classifier = classifier.NB_Classifier(classCount)
        self.classCount = classCount

        self.state = "Started"
        self.actionCount = 0
        self.actionCountByClass = [0.0] * classCount

        self.final_epsilon = final_epsilon
        self.alt_hist_alpha = alt_hist_alpha
        self.vario_hist_alpha = vario_hist_alpha

    def load(self, stored_dict):
        if self.classCount == len(stored_dict['actionCountByClass']):
            self.classifier.load(stored_dict)
            self.actionCount = stored_dict['actionCount']
            self.actionCountByClass = stored_dict['actionCountByClass']


    def save(self):
        save_dict = self.classifier.save()
        save_dict['actionCount'] = self.actionCount
        save_dict['actionCountByClass'] = self.actionCountByClass
        return save_dict


    def update_hist(self, h, v, mina, maxa, stepa, alpha=0.995):
        ix = int((max(mina, min(maxa, v))-mina)/stepa)
        for i in range(len(h)):
            if ix == i:
                h[i] = h[i]*alpha + (1-alpha)
            else:
                h[i] = h[i]*alpha

    def init_hist(self):
        self.vario_hist_short = [1/9] * 9
        self.alt_hist = [1/5] * 5

    def add_file(self, filename, classIx):
        self.init_hist()
        with open(filename) as f:
            lines = f.readlines()

        for l in lines:
            vs  = l.strip().split(",")
            alt,vario, control = [float(s) for s in vs[1:]]

            self.update_reading(alt, vario)

        self.train(classIx)

    def update_reading(self, alt, vario):
        self.update_hist(self.vario_hist_short, vario, -20, 20, 5, self.vario_hist_alpha)
        self.update_hist(self.alt_hist, alt, -25, 75, 25, self.alt_hist_alpha) 

    def binnify(self, v, mina=0, maxa=1, bins=3):
        v -= mina + 1e-6
        v /= (maxa - mina)
        v *= bins
        v = int(v)
        return v


    def make_features(self):
        features = [0.0] * 10
        for i,h in enumerate(self.vario_hist_short):
            ix = int(abs(i-4))
            features[ix] += h

        for i,h in enumerate(self.alt_hist):
            features[i+5] += h
        binned= [0] * 30
        for i,b in enumerate(features):
            bin_ = self.binnify(b)
            binned[i*3 + bin_] += 1


        return binned
        
    def train(self, classIx, reward=1):
        if reward == 1:
            #print("train:",self.make_features())
            self.classifier.train(self.make_features(), classIx)
            

    def recommend_proba(self):
        def get_item(v):
            return v[1]
        hist = self.make_features()
        #print(["%.2f"% h for h in hist])
        result = []

        epsilon = (10 - min(self.classifier.evidenceCount, 10))/10*(1 - self.final_epsilon) + self.final_epsilon 
        do_explore = random.random() < epsilon

        if do_explore:
            self.state = "explore"
            rec = random.randint(0, self.classifier.classCount-1)
            probs = [1/self.classifier.classCount] * self.classifier.classCount
        else:
            probs, count = self.classifier.classify(self.make_features())

            rec_ix = random.randint(0, 5)
            if rec_ix >= count:
                self.state = "explore1"
                rec = random.randint(0, self.classifier.classCount-1)
                probs = [1/self.classifier.classCount] * self.classifier.classCount
            else:
                self.state = "exploit"


                totalProb = 0.0
                for klass in range(self.classifier.classCount):
                    if self.actionCountByClass[klass] > 0:
                        probs[klass] += math.sqrt(math.log(self.actionCount)/self.actionCountByClass[klass])
                    else:
                        probs[klass] = 1.0
                    probs[klass] = min(probs[klass], 1.0)
                    totalProb += probs[klass]


                for klass in range(self.classifier.classCount):
                    probs[klass] = probs[klass] / totalProb

                choice = random.random()
                cum_prob = 0
                #print(choice, probs)
                rec = 0
                for i,p in enumerate(probs):
                    cum_prob += probs[i]
                    if choice < cum_prob:
                        rec = i
                        break

        self.actionCountByClass[rec] += 1
        self.actionCount += 1
        return rec, probs



    def recommend(self):
        rec, _ = self.recommend_proba()
        return rec
