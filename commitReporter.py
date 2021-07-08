from datetime import date
import os
import csv
from github import Github
from github.GithubException import GithubException

# API user check
# API token
ACCESS_TOKEN = "input personal access token in here"


class CommitData:

    # CSV파일 && 폴더 생성
    def makeCsvFile(self):
        # 폴더 생성
        d = date.today()
        path = './commit-report/{}'.format(d)
        try:
            if not os.path.exists(path):  # 해당 path에 폴더가 없을 시 생성
                os.makedirs(path)
        except OSError:
            print("Error message : Cannot create the directory {}".format(path))

        # CSV 파일 생성
        header = ["Repository-Name", "Commit-ID", "Date",
                  "Author", "Author-emil", "Commit-Message"]
        lastID = self.dataList[0][1]
        lastID = lastID[0:5]
        # CSV file 생성
        try:
            with open("{0}/{1}{2}~{3}.csv".format(path, self.repo.name, self.branch_name, lastID), "w", newline="", encoding="cp949") as file:
                writer = csv.writer(file)
                rowNum = 0
                writer.writerow(header)
                for row in self.dataList:
                    writer.writerow(row)
                    rowNum += 1
                print("Creation completed.({} commits)".format(rowNum))
        except Exception as err:
            print("Error message : {}".format(err))
            self.findCommitInList()

    # Commit ID 입력, 입력한 commit ~ 최신 commit 출력
    def findCommitInList(self):
        # Commit list에서 검색된 commit들을 출력할 data list에 저장
        def inputDataList(commitIdList, commitList):
            dataList = []
            if len(commitIdList) == 1:
                for index1, row1 in enumerate(commitList):
                    if commitIdList[0] in row1[1]:
                        for index2, row2 in enumerate(commitList):
                            if index2 <= index1:
                                dataList.append(row2)
                        break
                return dataList
            else:
                startIndex, endIndex = 0, 0
                for index, row in enumerate(commitList):
                    if commitIdList[1] in row[1]:
                        startIndex = index
                    if commitIdList[0] in row[1]:
                        endIndex = index + 1
                for index, row in enumerate(commitList):
                    if index in range(startIndex, endIndex):
                        dataList.append(row)
                return dataList
        try:
            self.dataList = []
            inputCommitID = input(
                'Input commit ID(input <all>-->get all) : ').split(" ")

            if inputCommitID[0] == "all":  # all 입력 시
                print("print all commits\n")
                self.dataList = self.commitList
            elif len(inputCommitID) == 1:  # 1개의 commit ID 입력 시
                if len(inputCommitID[0]) < 6:
                    print("At least 6 characters required\n")
                    self.findCommitInList()
                else:
                    self.dataList = inputDataList(
                        inputCommitID, self.commitList)
            elif len(inputCommitID) == 2:  # 2개의 commit ID 입력 시
                if len(inputCommitID[0]) < 6 or len(inputCommitID[1]) < 6:
                    print("At least 6 characters required\n")
                    self.findCommitInList()
                else:
                    self.dataList = inputDataList(
                        inputCommitID, self.commitList)
        except Exception as err:
            print("Error message : {}, please try again".format(err))
            self.selectBranch()
        else:
            if len(self.dataList) == 0:
                print("No search result\n")
                self.findCommitInList()  # 일치하는 Commit ID가 없을 시 재귀
            else:
                self.makeCsvFile()

    # Repo의 모든 commit data 저장
    def makeCommitlist(self):
        self.commits = self.repo.get_commits(sha=self.branch_name)
        self.commitList = []
        for commit in self.commits:
            temp_list = [
                self.repo.name,
                commit.sha,
                str(commit.commit.author.date),
                commit.commit.author.name,
                commit.commit.author.email,
                commit.commit.message]
            self.commitList.append(temp_list)
        self.findCommitInList()

    def selectBranch(self, branch_list):
        try:
            inputBranchName = input("Input branch name : ")
            if inputBranchName in branch_list:
                self.branch_name = inputBranchName
                self.makeCommitlist()
            else:
                print("Branch not found, please try again.")
                self.selectBranch(branch_list)
        except Exception as err:
            print("Error message : {}, please try again".format(err))
            self.selectBranch(branch_list)

    # 입력한 Repo 저장
    def selectRepo(self):
        # Repository 이름 입력
        try:
            inputRepoName = input("Input repository name : ")
            for repo in self.repos:
                if repo.name == inputRepoName:
                    self.repo = repo
            self.branches = self.repo.get_branches()
            branchNameList = []
            print("<Branch-list>")
            for branch in self.branches:
                print(branch.name)
                branchNameList.append(branch.name)
            self.selectBranch(branchNameList)
        except Exception:
            print("Error message : Cannot found [{}], please try again".format(
                inputRepoName))
            self.selectRepo()

    # 입력한 Org를 찾고, 해당 Org의 Repo list 출력
    def findOrg(self):
        # Organization 이름 입력
        try:
            inputOrgName = input("Input organizaion name : ")
            self.org = self.g.get_organization(inputOrgName)
        except GithubException as err:
            print("Error message : {}, please try again".format(
                err.data['message']))
            self.findOrg()
        else:
            self.repos = self.org.get_repos()
            for repo in self.repos:
                print("repo_name: {0}\nprivate: {1}\n".format(
                    repo.name, repo.private))
            self.selectRepo()

    def __init__(self, token):
        self.g = Github(token)
        self.findOrg()


if __name__ == '__main__':
    CommitData(token=ACCESS_TOKEN)
