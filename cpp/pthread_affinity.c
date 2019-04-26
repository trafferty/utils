#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

bool done;

void* DoWork(void* args) {
    while (!done)
    {
      printf("ID: %lu, CPU: %d\n", pthread_self(), sched_getcpu());
      usleep(1*1000);
    }

    return 0;
}

int main() {   

    int numberOfProcessors = sysconf(_SC_NPROCESSORS_ONLN);
    printf("Number of processors: %d\n", numberOfProcessors);

    pthread_t threads[numberOfProcessors];

    pthread_attr_t attr;
    cpu_set_t cpus;
    pthread_attr_init(&attr);

    done = false;

    for (int i = 0; i < numberOfProcessors; i++) {
       CPU_ZERO(&cpus);
       CPU_SET(i, &cpus);
       pthread_attr_setaffinity_np(&attr, sizeof(cpu_set_t), &cpus);
       pthread_create(&threads[i], &attr, DoWork, NULL);
    }

    usleep(1*1000*1000);

    done = true;
    
    for (int i = 0; i < numberOfProcessors; i++) {
        pthread_join(threads[i], NULL);
    }

    return 0;
}