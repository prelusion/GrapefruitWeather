ARG DEBUG=FALSE

FROM gradle:6.0-jdk11 AS build
COPY --chown=gradle:gradle . /home/gradle/src
WORKDIR /home/gradle/src
RUN gradle build --no-daemon

FROM gradle:6.0-jre11
RUN mkdir /app
COPY --from=build /home/gradle/src/build/libs/weatherstation-1.0.jar /app/application.jar
ENTRYPOINT ["java", "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005", "-jar","/app/application.jar"]

EXPOSE 7789
EXPOSE 5005
