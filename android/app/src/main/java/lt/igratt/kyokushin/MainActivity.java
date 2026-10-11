package lt.igratt.kyokushin;

import android.os.Bundle;
import android.view.WindowManager;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(RestTimerPlugin.class);
        super.onCreate(savedInstanceState);
        // Workout app: the screen must not go dark between sets.
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }

    @Override
    public void onResume() {
        super.onResume();
        RestTimerCore.foreground = true;
    }

    @Override
    public void onPause() {
        RestTimerCore.foreground = false;
        super.onPause();
    }
}
