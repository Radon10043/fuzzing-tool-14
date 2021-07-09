main.exe:main.o CheckData.o
	g++ -o main.exe main.o CheckData.o -lws2_32
main.o:main.cpp Datagram.h Trajectory.h
	g++ -c main.cpp 
CheckData.o:CheckData.cpp Datagram.h Trajectory.h
	g++ -c CheckData.cpp
clean:
	rm *.o *.exe