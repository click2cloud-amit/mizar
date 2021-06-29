from kubernetes import client, config
import time

def main():
    config.load_incluster_config()
    apps = client.AppsV1Api()
    print('inside waiter')
    while True:
        test1 = apps.read_namespaced_daemon_set_status(
            'mizar-daemon', 'default')
        if test1.status.number_ready >= 1:
            print('waiting to daemon up')
            break
        time.sleep(1)


if __name__ == '__main__':
    main()

