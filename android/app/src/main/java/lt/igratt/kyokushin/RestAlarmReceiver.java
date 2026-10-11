package lt.igratt.kyokushin;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** Wakes up at the end of a rest (exact alarm) and rings, even when the app is in the background. */
public class RestAlarmReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        RestTimerCore.fire(context.getApplicationContext(), intent, goAsync());
    }
}
