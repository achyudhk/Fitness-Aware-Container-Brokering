import subprocess
import time

user_name = 'achyudhk'
num_nodes = 1
zones = ['asia-east1-a',' asia-east1-b',' asia-east1-c','asia-northeast1-a',' asia-northeast1-c',' asia-northeast1-b',' europe-west1-c',' europe-west1-b',' europe-west1-d',' us-central1-c',' us-central1-b',' us-central1-f',' us-central1-a',' us-east1-d','us-east1-c',' us-east1-b',' us-west1-a',' us-west1-b']
machine_types = ['f1-micro','g1-small','n1-highcpu-2','n1-highcpu-4','n1-highcpu-8','n1-highmem-2','n1-highmem-4','n1-highmem-8','n1-standard-1','n1-standard-2','n1-standard-4','n1-standard-8']
cluster_name = "lp-%s-%s-%s" %(machine_types[8], zones[0], str(num_nodes))

# subprocess.run('gcloud auth application-default login', shell=True)
subprocess.run('gcloud container clusters create %s -m %s -z %s --num-nodes=%s' % (cluster_name, machine_types[8], zones[0], str(num_nodes)), shell=True)
subprocess.run('gcloud container clusters get-credentials ' + cluster_name, shell=True)
subprocess.run('kubectl run linpack-node --image=asia.gcr.io/my-project-1470428279137/linpack --port=8080', shell=True)
subprocess.run('kubectl get deployments && kubectl get pods', shell=True)

node_desc = dict()
active_nodes = list()
response = subprocess.run('kubectl describe nodes', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
for line in response.stdout.split('\n'):
    if 'Name:' in line:
        node_desc['Name'] = line.split(':')[1].strip()
        node_desc['Task'] = node_desc['Name'].split('-')[1]
    if 'instance-type=' in line:
        node_desc['Type'] = line.split("=")[-1]
    if 'zone=' in line:
        node_desc['Zone'] = line.split("=")[-1]
    if 'Addresses:' in line:
        node_desc['IP'] = line.split(':')[1].strip().split(',')[1]
        active_nodes.append(node_desc)

print("Waiting for Linpack benchmark to execute...")
time.sleep(300)

for node_desc in active_nodes:
    cmd_to_exec = "'docker logs $(docker ps -l -q)'"
    response = subprocess.Popen(['ssh -i "~/.ssh/google_compute_engine" -o StrictHostKeyChecking=no %s@%s ' % (user_name, node_desc['IP']) + cmd_to_exec],
                           shell=True, universal_newlines=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

    with open("data_linpack/gcp_%s_%s.txt" % (node_desc['Type'], node_desc['Zone']), 'w') as txt_file:
        txt_file.write("".join(response.stdout.readlines()))


subprocess.Popen('gcloud container clusters delete %s' % cluster_name, shell=True)