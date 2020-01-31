package nl.hanze.weatherstation;

import lombok.val;

import java.io.File;
import java.util.*;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class FileHelper {
    public static List<Integer> extractExtensionSequences(String path, String extension) {
        val files = new File(path).listFiles();

        if (files == null) {
            return new ArrayList<>();
        }

        val pattern = Pattern.compile("^([0-9]+)\\." + extension + "$");

        List<Integer> sequences = Arrays.stream(files)
                .map(f -> {
                    val matcher = pattern.matcher(f.getName());

                    return matcher.find() ? matcher.group(1) : null;
                })
                .filter(Objects::nonNull)
                .map(Integer::parseInt)
                .collect(Collectors.toList());

        Collections.reverse(sequences);

        return sequences;
    }
}
