# NKP Pre-deployment - port connectivity check 

## Overview
This role is used to verify the port requirements for deploying NKP management cluster on a Nutanix infrastructure.


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
    - rathnaarun77.nkp_checks
  environment:
        ANSIBLE_HOST_KEY_CHECKING: "False"
        image_url:                                       # url to download image from nutanix portal 
        IMAGE_NAME:                                      # Image name - corresponding to the above url
        SSH_PUBLIC_KEY:                                  # SSH key of the local machine,used by ansible to connect to the test VM
        NUTANIX_ENDPOINT:                                # Prism Central IP address
        NUTANIX_USER: admin                              # Prism Central username
        NUTANIX_PASSWORD: ''                             # Prism Central password
        NUTANIX_PORT: 9440                               # Prism Central port (default: 9440)                                          
        NUTANIX_PRISM_ELEMENT_CLUSTER_NAME:              # Prism Element cluster name - Ex: PHX-POC207
        CONTROL_SUBNET:                                  # controlplane subnet name
        WORKER_SUBNET:                                   # worker subnet name
        NUTANIX_STORAGE_CONTAINER_NAME:                  # Change to your preferred Prism storage container
```

    > ⚠️ **Note:** All the variables are mandatory.

4. Finally, to trigger the playbook, run the following command:
    ```sh
    ansible-playbook -i inventory.ini playbook.yml
    ```

5. Once the playbook completes without any errors, you will get the NKP dashboard URL and the login credentials as output of the final task.

Disclaimer:

The views and opinions expressed in this repository are my own and do not necessarily reflect those of any company or organization. The information provided is based on personal experience and research. It is presented as-is without any warranties. For official guidance, please refer to the official documentation or support channels.

## License
MIT