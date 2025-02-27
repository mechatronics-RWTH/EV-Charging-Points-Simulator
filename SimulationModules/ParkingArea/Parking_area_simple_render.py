import logging 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arrow
from SimulationModules.ParkingArea.ParkingAreaElements import ParkingSpot, Obstacle
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


logger = logging.getLogger(__name__)

def render_parking_area(parking_area: ParkingArea, interval: float = 1.0):
    size_x = parking_area.parking_area_size[0]
    size_y = parking_area.parking_area_size[1]

    xs = np.arange(0, size_x + 1, 1, dtype=int)
    ys = np.arange(0, size_y + 1, 1, dtype=int)
    #at first, we deaktivate hese annoying debug msgs:
    mpl_logger = logging.getLogger('matplotlib')
    mpl_logger.setLevel(logging.WARNING)
    plt.figure(figsize=(6.4/10*size_x, 4.8/4*size_x))
    ax = plt.gca()
    # grid "shades" (boxes)
    w, h = xs[1] - xs[0], ys[1] - ys[0]

    for i, x in enumerate(xs[:-1]):
        for j, y in enumerate(ys[:-1]):
            # if i % 2 == j % 2:  # racing flag style
            #     ax.add_patch(Rectangle((x, y), w, h, fill=True, color='#008610', alpha=.1))
            field = parking_area._get_field_by_position([x, y])
            if isinstance(field, ParkingSpot):
                # ax.add_patch(Arrow(x + 0.25, y + h / 2, w * 0.5, 0))
                txt = f"P"
                plt.text(x + w / 2, y + h / 2, txt,
                            ha='center',
                            va='center',
                            size='xx-large',
                            rotation='vertical')
            elif isinstance(field, EntrencePoint):
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='g', alpha=.1))
                txt = f"({x},{y})"
                plt.text(x + w / 2, y + h / 2, txt, ha='center', va='center')
            elif isinstance(field, ExitPoint):
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='r', alpha=.1))
                txt = f"({x},{y})"
                plt.text(x + w / 2, y + h / 2, txt, ha='center', va='center')
            elif isinstance(field, Obstacle):
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='k', alpha=1))
                txt = f"({x},{y})"
                plt.text(x + w / 2, y + h / 2, txt, ha='center', va='center',color='w')
            else:
                txt = f"({x},{y})"
                plt.text(x + w / 2, y + h / 2, txt, ha='center', va='center')

            if field.has_charging_station():
                logo = field.charger.logo
                imagebox = OffsetImage(logo, zoom=0.08)
                # Annotation box for solar pv logo
                # Container for the imagebox referring to a specific position *xy*.
                ab = AnnotationBbox(imagebox, (x + w / 4, y + h / 2), frameon=False)
                ax.add_artist(ab)
            if field.has_parked_vehicle():
                car_logo = field.vehicle_parked.logo
                imagebox = OffsetImage(car_logo, zoom=0.04)
                # Annotation box for solar pv logo
                # Container for the imagebox referring to a specific position *xy*.
                ab = AnnotationBbox(imagebox, (x + w / 1.8, y + h / 2), frameon=False)
                ax.add_artist(ab)

            if parking_area.get_gini_by_field_index(field.index) is not None:
                gini=parking_area.get_gini_by_field_index(field.index)
                gini_logo = gini.logo
                imagebox = OffsetImage(gini_logo, zoom=0.04)
                # Annotation box for solar pv logo
                # Container for the imagebox referring to a specific position *xy*.
                ab = AnnotationBbox(imagebox, (x + w / 1.8, y + h / 2), frameon=False)
                ax.add_artist(ab)

    # grid lines
    for x in xs:
        plt.plot([x, x], [ys[0], ys[-1]], color='black', alpha=.33, linestyle=':')
    for y in ys:
        plt.plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

    
    plt.show(block=False)

    if interval is not None:
        logger.info(f"Parking Area rendered for {interval} seconds",interval)
        plt.pause(interval)
        plt.close()

