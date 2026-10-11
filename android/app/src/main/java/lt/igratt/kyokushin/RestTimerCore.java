package lt.igratt.kyokushin;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.AlarmManager;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.res.AssetFileDescriptor;
import android.media.AudioAttributes;
import android.media.AudioFocusRequest;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.os.VibratorManager;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
import androidx.core.content.ContextCompat;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Native side of the rest timer.
 * - While resting: a silent notification with a live countdown (visible in the shade and on the lock screen).
 * - At the end: an exact alarm plays the beep and vibrates, even when the app is hidden or the screen is off,
 *   and (when the app is not on screen) posts a "rest is over" notification.
 */
final class RestTimerCore {

    static final String CH_COUNTDOWN = "rest_countdown";
    static final String CH_DONE = "rest_done";
    static final int ID_COUNTDOWN = 41;
    static final int ID_DONE = 42;
    static final int REQ_ALARM = 4101;
    static final int REQ_OPEN = 4102;

    /** Set by MainActivity: is the app on screen right now? */
    static volatile boolean foreground = false;

    private RestTimerCore() {}

    static void ensureChannels(Context ctx) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;
        NotificationManager nm = ctx.getSystemService(NotificationManager.class);
        if (nm == null) return;
        NotificationChannel countdown = new NotificationChannel(CH_COUNTDOWN, "Poilsio laikmatis", NotificationManager.IMPORTANCE_LOW);
        countdown.setDescription("Kiek liko poilsio, kai programa paslėpta");
        countdown.setShowBadge(false);
        countdown.setSound(null, null);
        countdown.enableVibration(false);
        countdown.setLockscreenVisibility(NotificationCompat.VISIBILITY_PUBLIC);
        nm.createNotificationChannel(countdown);
        NotificationChannel done = new NotificationChannel(CH_DONE, "Poilsio pabaiga", NotificationManager.IMPORTANCE_HIGH);
        done.setDescription("Pranešimas, kai poilsis baigiasi");
        done.setSound(null, null); // the app plays its own beep
        done.enableVibration(false); // and vibrates itself
        done.setLockscreenVisibility(NotificationCompat.VISIBILITY_PUBLIC);
        nm.createNotificationChannel(done);
    }

    private static boolean canNotify(Context ctx) {
        if (Build.VERSION.SDK_INT >= 33
            && ContextCompat.checkSelfPermission(ctx, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            return false;
        }
        return NotificationManagerCompat.from(ctx).areNotificationsEnabled();
    }

    private static PendingIntent openApp(Context ctx) {
        Intent open = new Intent(ctx, MainActivity.class);
        open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        return PendingIntent.getActivity(ctx, REQ_OPEN, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    @SuppressLint("MissingPermission")
    static void schedule(
        Context ctx,
        long endAt,
        String title,
        String text,
        String doneTitle,
        String doneText,
        boolean sound,
        boolean vibrate
    ) {
        ensureChannels(ctx);
        Intent alarm = new Intent(ctx, RestAlarmReceiver.class);
        alarm.putExtra("doneTitle", doneTitle);
        alarm.putExtra("doneText", doneText);
        alarm.putExtra("sound", sound);
        alarm.putExtra("vibrate", vibrate);
        PendingIntent pi = PendingIntent.getBroadcast(ctx, REQ_ALARM, alarm, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        if (am != null) {
            boolean exact = Build.VERSION.SDK_INT < Build.VERSION_CODES.S || am.canScheduleExactAlarms();
            if (exact) am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, endAt, pi);
            else am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, endAt, pi);
        }

        NotificationManagerCompat nm = NotificationManagerCompat.from(ctx);
        nm.cancel(ID_DONE);
        if (!canNotify(ctx)) return;
        long left = Math.max(1000L, endAt - System.currentTimeMillis());
        NotificationCompat.Builder b = new NotificationCompat.Builder(ctx, CH_COUNTDOWN)
            .setSmallIcon(R.drawable.ic_stat_timer)
            .setContentTitle(title)
            .setContentText(text)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setSilent(true)
            .setShowWhen(true)
            .setWhen(endAt)
            .setUsesChronometer(true)
            .setChronometerCountDown(true)
            .setTimeoutAfter(left + 1500L)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setContentIntent(openApp(ctx));
        try {
            nm.notify(ID_COUNTDOWN, b.build());
        } catch (SecurityException ignored) {
            // notifications not allowed: the alarm still rings
        }
    }

    static void cancel(Context ctx) {
        Intent alarm = new Intent(ctx, RestAlarmReceiver.class);
        PendingIntent pi = PendingIntent.getBroadcast(ctx, REQ_ALARM, alarm, PendingIntent.FLAG_NO_CREATE | PendingIntent.FLAG_IMMUTABLE);
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        if (pi != null && am != null) {
            am.cancel(pi);
            pi.cancel();
        }
        NotificationManagerCompat nm = NotificationManagerCompat.from(ctx);
        nm.cancel(ID_COUNTDOWN);
        nm.cancel(ID_DONE);
    }

    /** Called by RestAlarmReceiver when the rest is over. */
    @SuppressLint("MissingPermission")
    static void fire(Context ctx, Intent intent, BroadcastReceiver.PendingResult pending) {
        NotificationManagerCompat nm = NotificationManagerCompat.from(ctx);
        nm.cancel(ID_COUNTDOWN);
        if (intent.getBooleanExtra("vibrate", true)) vibrate(ctx);
        if (!foreground && canNotify(ctx)) {
            ensureChannels(ctx);
            NotificationCompat.Builder b = new NotificationCompat.Builder(ctx, CH_DONE)
                .setSmallIcon(R.drawable.ic_stat_timer)
                .setContentTitle(intent.getStringExtra("doneTitle"))
                .setContentText(intent.getStringExtra("doneText"))
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setCategory(NotificationCompat.CATEGORY_ALARM)
                .setAutoCancel(true)
                .setTimeoutAfter(10 * 60 * 1000L)
                .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
                .setContentIntent(openApp(ctx));
            try {
                nm.notify(ID_DONE, b.build());
            } catch (SecurityException ignored) {
                // ignore
            }
        }
        if (intent.getBooleanExtra("sound", true)) playBeep(ctx, pending);
        else if (pending != null) pending.finish();
    }

    private static void vibrate(Context ctx) {
        Vibrator v;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            VibratorManager vm = (VibratorManager) ctx.getSystemService(Context.VIBRATOR_MANAGER_SERVICE);
            v = vm != null ? vm.getDefaultVibrator() : null;
        } else {
            v = (Vibrator) ctx.getSystemService(Context.VIBRATOR_SERVICE);
        }
        if (v == null || !v.hasVibrator()) return;
        long[] pattern = { 0, 400, 150, 400, 150, 900 };
        // Alarm usage: Android lets alarm vibrations through while the app is in the background.
        AudioAttributes attrs = new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_ALARM).build();
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) v.vibrate(VibrationEffect.createWaveform(pattern, -1), attrs);
        else v.vibrate(pattern, -1, attrs);
    }

    /** Plays res/raw/rest_end.wav on the media stream (same volume as music; music ducks briefly). */
    private static void playBeep(Context ctx, BroadcastReceiver.PendingResult pending) {
        final AudioManager am = (AudioManager) ctx.getSystemService(Context.AUDIO_SERVICE);
        final AudioAttributes attrs = new AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_MEDIA)
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
            .build();
        final AudioFocusRequest focus = Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
            ? new AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK).setAudioAttributes(attrs).build()
            : null;
        if (am != null && focus != null) am.requestAudioFocus(focus);

        final MediaPlayer mp = new MediaPlayer();
        final AtomicBoolean finished = new AtomicBoolean(false);
        final Runnable done = () -> {
            if (!finished.compareAndSet(false, true)) return;
            try {
                mp.release();
            } catch (Exception ignored) {
                // ignore
            }
            if (am != null && focus != null) am.abandonAudioFocusRequest(focus);
            if (pending != null) pending.finish();
        };
        new Handler(Looper.getMainLooper()).postDelayed(done, 8000L);
        try {
            mp.setAudioAttributes(attrs);
            AssetFileDescriptor afd = ctx.getResources().openRawResourceFd(R.raw.rest_end);
            mp.setDataSource(afd.getFileDescriptor(), afd.getStartOffset(), afd.getLength());
            afd.close();
            mp.setOnCompletionListener(p -> done.run());
            mp.setOnErrorListener((p, what, extra) -> {
                done.run();
                return true;
            });
            mp.prepare();
            mp.start();
        } catch (Exception e) {
            done.run();
        }
    }
}
