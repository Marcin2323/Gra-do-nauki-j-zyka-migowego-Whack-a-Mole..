from mod import HandshapeRecognizer
import statistics

class Validator:
    def __init__(self,dataset,datasetPath,subjects,gestures):
        self.dataset = dataset
        self.datasetPath = datasetPath
        self.subjects = subjects
        self.gestures = gestures

    def losoCrossValidation(self):
        hr_check = HandshapeRecognizer(self.dataset, self.datasetPath, self.subjects, self.gestures, check=True)
        accuracies = []
        # +1 because of non-class case
        confusionMatrix = [[0 for _ in range(len(hr_check.classesUnique)+3)] for _ in range(len(hr_check.classesUnique)+2)]
        #create headers (labels)
        confusionMatrix[0] = [""] + hr_check.classesUnique + ["", ""]
        confusionMatrix[-1] = [""] + hr_check.classesUnique + ["", ""]
        for l in range(len(hr_check.classesUnique)):
            confusionMatrix[l+1][0] = hr_check.classesUnique[l]
            confusionMatrix[l+1][-1] = hr_check.classesUnique[l]
        confusionMatrix[0][-2] = "no"
        confusionMatrix[-1][-2] = "no"

        for subject in hr_check.subjectsUnique:
            trainingSubjects = hr_check.subjectsUnique.copy()
            trainingSubjects.remove(subject)
            hr_test = HandshapeRecognizer(self.dataset, self.datasetPath, [subject])
            hr_train = HandshapeRecognizer(self.dataset, self.datasetPath, trainingSubjects)
            #self.calculateNormalizedFeatures(hr_test,hr_train)
            hr_train.train()
            correctAnswers = 0
            for i, unknown in enumerate(hr_test.templates):
                predictedLabel = hr_train.run(unknown)
                if predictedLabel == hr_test.classes[i]:
                    correctAnswers += 1
                # number of predicted class
                if predictedLabel != "":
                    indClass_pred = list(hr_train.classRepresentatives.keys()).index(predictedLabel)+1
                else:
                    indClass_pred = len(hr_train.classRepresentatives)+1
                # number of target class
                indClass_targ = list(hr_train.classRepresentatives.keys()).index(hr_test.classes[i])+1
                confusionMatrix[indClass_targ][indClass_pred] += 1
            accuracies.append( correctAnswers / len(hr_test.templates) * 100 )
        return (statistics.mean(accuracies), statistics.stdev(accuracies), confusionMatrix, accuracies, hr_check.subjectsUnique)

    def calculateNormalizedFeatures(self,hr_test,hr_train):
        mins_x = [0]*21
        mins_y = [0]*21
        mins_z = [0]*21
        maxes_x = [0]*21
        maxes_y = [0]*21
        maxes_z = [0]*21
        #find mins and maxes
        for t in range(len(hr_train.templates)):
            for i in range(len(hr_train.templates[t].nodesX_world)):
                if t==0:
                    mins_x[i] = hr_train.templates[t].nodesX_world[i]
                    mins_y[i] = hr_train.templates[t].nodesY_world[i]
                    mins_z[i] = hr_train.templates[t].nodesZ_world[i]
                    maxes_x[i] = hr_train.templates[t].nodesX_world[i]
                    maxes_y[i] = hr_train.templates[t].nodesY_world[i]
                    maxes_z[i] = hr_train.templates[t].nodesZ_world[i]
                elif hr_train.templates[t].nodesX_world[i] < mins_x[i]:
                    mins_x[i] = hr_train.templates[t].nodesX_world[i]
                elif hr_train.templates[t].nodesY_world[i] < mins_y[i]:
                    mins_y[i] = hr_train.templates[t].nodesY_world[i]
                elif hr_train.templates[t].nodesZ_world[i] < mins_z[i]:
                    mins_z[i] = hr_train.templates[t].nodesZ_world[i]
                elif hr_train.templates[t].nodesX_world[i] > maxes_x[i]:
                    maxes_x[i] = hr_train.templates[t].nodesX_world[i]
                elif hr_train.templates[t].nodesY_world[i] > maxes_y[i]:
                    maxes_y[i] = hr_train.templates[t].nodesY_world[i]
                elif hr_train.templates[t].nodesZ_world[i] > maxes_z[i]:
                    maxes_z[i] = hr_train.templates[t].nodesZ_world[i]

        for t in range(len(hr_train.templates)):
            hr_train.templates[t].nodesX_world_norm = hr_train.templates[t].nodesX_world.copy()
            hr_train.templates[t].nodesY_world_norm = hr_train.templates[t].nodesY_world.copy()
            hr_train.templates[t].nodesZ_world_norm = hr_train.templates[t].nodesZ_world.copy()
            for i in range(len(hr_train.templates[t].nodesX_world)):
                if maxes_x[i] - mins_x[i] != 0:
                    hr_train.templates[t].nodesX_world_norm[i] = (hr_train.templates[t].nodesX_world[i] - mins_x[i]) / (maxes_x[i]-mins_x[i])
                if maxes_y[i] - mins_y[i] != 0:
                    hr_train.templates[t].nodesY_world_norm[i] = (hr_train.templates[t].nodesY_world[i] - mins_y[i]) / (maxes_y[i]-mins_y[i])
                if maxes_z[i] - mins_z[i] != 0:
                    hr_train.templates[t].nodesZ_world_norm[i] = (hr_train.templates[t].nodesZ_world[i] - mins_z[i]) / (maxes_z[i]-mins_z[i])

        for t in range(len(hr_test.templates)):
            hr_test.templates[t].nodesX_world_norm = hr_test.templates[t].nodesX_world.copy()
            hr_test.templates[t].nodesY_world_norm = hr_test.templates[t].nodesY_world.copy()
            hr_test.templates[t].nodesZ_world_norm = hr_test.templates[t].nodesZ_world.copy()
            for i in range(len(hr_test.templates[t].nodesX_world)):
                if maxes_x[i] - mins_x[i] != 0:
                    hr_test.templates[t].nodesX_world_norm[i] = (hr_test.templates[t].nodesX_world[i] - mins_x[i]) / (maxes_x[i] - mins_x[i])
                if maxes_y[i] - mins_y[i] != 0:
                    hr_test.templates[t].nodesY_world_norm[i] = (hr_test.templates[t].nodesY_world[i] - mins_y[i]) / (maxes_y[i] - mins_y[i])
                if maxes_z[i] - mins_z[i] != 0:
                    hr_test.templates[t].nodesZ_world_norm[i] = (hr_test.templates[t].nodesZ_world[i] - mins_z[i]) / (maxes_z[i] - mins_z[i])