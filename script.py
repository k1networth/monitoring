import json
import subprocess

def get_instances():
    result = subprocess.run(
        ['yc', 'compute', 'instance', 'list', '--format', 'json'], 
        stdout=subprocess.PIPE
    )
    return json.loads(result.stdout)

def generate_prometheus_targets():
    instances = get_instances()
    targets = []

    for instance in instances:
        name = instance['name']
        status = instance['status']
        if status != "RUNNING":
            continue

        labels = instance.get('labels', {})
        instance_label = labels.get('instance', name)

        for nic in instance.get('network_interfaces', []):
            ip = nic.get('primary_v4_address', {}).get('one_to_one_nat', {}).get('address')
            if ip:
                targets.append({
                    "targets": [f"{ip}:9100"],
                    "labels": {"instance": instance_label}
                })
    
    return targets

def write_to_file(targets):
    with open('/home/yuuarai/monitoring/targets.json', 'w') as f:
        json.dump(targets, f, indent=4)

if __name__ == "__main__":
    write_to_file(generate_prometheus_targets())
    print("targets.json обновлен!")

