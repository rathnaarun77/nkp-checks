# NKP Pre-deployment - port connectivity check 

## Overview
This Ansible role is used to verify the port requirements for deploying Nutanix Kubernetes Platform(NKP) cluster on a Nutanix infrastructure.


## Usage

### Pre-requisites:
Since we are deploying in a Nutanix environment, install the `nutanix.ncp` ansible collection by running the below command on your control node:  

    ansible-galaxy collection install nutanix.ncp

### Steps:
1. Download this role to the Ansible control plane from Ansible Galaxy by running the following command:
    ```sh
    ansible-galaxy role install rathnaarun77.nkp_checks
    ```

2. Create or download the `inventory.ini` file from this repo and pass it while you run the Ansible playbook, it just contains the localhost so no modifications required.
   ```yaml
   [localhost]
   localhost ansible_connection=local
   ```

3. Below is a sample `playbook.yml` file utilising this role:
```yaml
---
- hosts: all
  gather_facts: no
  roles:
    - nkp-checks
  environment:
    ANSIBLE_HOST_KEY_CHECKING: "False"
  vars:
    IMAGE_NAME:                                      # NKP rocky image name(don't use cis image)
    image_url: ""                                    # URL from nutanix portal for the image name specified above
    SSH_PUBLIC_KEY: ""                               # SSH key of the local machine, where you run the ansible playbook           
    NUTANIX_ENDPOINT:                                # Prism Central IP address
    NUTANIX_USER: admin                              # Prism Central username
    NUTANIX_PASSWORD: ''                             # Keep the password enclosed between single quotes - Ex: 'password'                                      
    NUTANIX_PRISM_ELEMENT_CLUSTER_NAME:              # Prism Element cluster name
    CONTROL_SUBNET:                                  # contorlplane subnet name as per prism
    WORKER_SUBNET:                                   # worker node pool subnet as per prism
    NUTANIX_STORAGE_CONTAINER_NAME:                  # The test VMs will be deployed here
    DS_IP:                                           # Dataservice IP of prism element
    airgapped: false                                 # Set to true if airgapped, also ensure to upload the VM image manually
    #management_cluster: "true"                      # If you are running pre-checks for management cluster and want to also check connectivity to workload clusters, then set management_cluster as true and also specify the workload clusters, in specified format.
    #workload_cluster_subnets:
    # - ["pe-cluster1", "workload_subnet1"]        
    # - ["pe-cluster2", "workload_subnet2"]
```

    > ⚠️ Note: This script works for both management and workload clusters.

    1. To use it for a management cluster, set the management_cluster flag to true and provide the list of workload clusters you want to deploy from it.

    2. If you're running the script on a management cluster and don't need to check connectivity with the workload clusters, set the management_cluster flag to false. You can still run the script for the management cluster in this case.

    3. Connectivity between the management cluster and workload clusters can only be checked when the management_cluster flag is set to true and is not applicable for workload clusters.

4. Finally, to trigger the playbook, run the following command:
    ```sh
    ansible-playbook -i inventory.ini playbook.yml
    ```

5. Once the playbook completes without any errors, you will get the final nkp_checks_report.html in the same directory.


## ⚙️ Ideal Usage

1. First, run the script for the **management cluster**, setting the `management_cluster` flag to `true` and specifying all the workload clusters.
2. Afterward, run the script individually for each **workload cluster**.

Disclaimer:

The views and opinions expressed in this repository are my own and do not necessarily reflect those of any company or organization. The information provided is based on personal experience and research. It is presented as-is without any warranties. For official guidance, please refer to the official documentation or support channels.

## License
MIT