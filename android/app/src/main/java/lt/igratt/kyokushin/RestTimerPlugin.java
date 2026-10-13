package lt.igratt.kyokushin;

import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Build;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/** JavaScript bridge for the rest timer (see src/native.ts → restTimer). */
@CapacitorPlugin(name = "RestTimer")
public class RestTimerPlugin extends Plugin {

    /** Called when a workout starts: creates the channels and asks for notification permission (Android 13+). */
    @PluginMethod
    public void prepare(PluginCall call) {
        RestTimerCore.ensureChannels(getContext());
        if (
            Build.VERSION.SDK_INT >= 33 &&
            getActivity() != null &&
            ContextCompat.checkSelfPermission(getContext(), Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(getActivity(), new String[] { Manifest.permission.POST_NOTIFICATIONS }, 4103);
        }
        call.resolve();
    }

    @PluginMethod
    public void start(PluginCall call) {
        Object end = call.getData().opt("endAt");
        long endAt = end instanceof Number ? ((Number) end).longValue() : 0L;
        if (endAt <= System.currentTimeMillis()) {
            call.resolve();
            return;
        }
        RestTimerCore.schedule(
            getContext(),
            endAt,
            call.getString("title", "Poilsis"),
            call.getString("text", ""),
            call.getString("doneTitle", "Poilsis baigėsi"),
            call.getString("doneText", ""),
            Boolean.TRUE.equals(call.getBoolean("sound", true)),
            Boolean.TRUE.equals(call.getBoolean("vibrate", true)),
            "short".equals(call.getString("tone", "rest"))
        );
        call.resolve();
    }

    @PluginMethod
    public void cancel(PluginCall call) {
        RestTimerCore.cancel(getContext());
        call.resolve();
    }
}
