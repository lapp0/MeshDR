import argparse
import pathlib
import numpy as np
from pygem import FFD
import time
import os

import matplotlib.pyplot as plt

from stl.mesh import Mesh
from mpl_toolkits import mplot3d


parser = argparse.ArgumentParser(description='Generate random mesh deformations.')
parser.add_argument('--mesh', type=str, help='Base file to deform.')
parser.add_argument('--outpath', type=pathlib.Path, default='./results', help='Path of generated meshes.')
parser.add_argument('--count', type=int, default=1000, help='Number of meshes generated.')
parser.add_argument('--std', type=float, default=0.1, help='Standard deviation of randomly placed control points.')
parser.add_argument('--control', type=int, default=3, help='Control points per dimension (totals control points is the cube of this arg).')
parser.add_argument('--demo', default=False, action='store_true', help='Demo mode: dont save stls, just show plots of the base and the first generated stl.')

args = parser.parse_args()


class StlMesh:
    def __init__(self, stl):
        self.stl = stl

        self.point_cloud = np.array([
            np.concatenate(self.stl.x),
            np.concatenate(self.stl.y),
            np.concatenate(self.stl.z)
        ]).T
        self.min_point = self.point_cloud.min(0)
        self.max_point = self.point_cloud.max(0)

    @classmethod
    def from_file(cls, stl_path):
        return cls(
            Mesh.from_file(stl_path)
        )

    def generate_new_from_point_cloud(self, point_cloud):
        # assumes point cloud is ordered into groups of 3 such that they form triangles
        new_stl = Mesh(self.stl.data)
        new_stl.x = np.array(np.array_split(
            point_cloud.T[0],
            len(point_cloud) / 3
        ))
        new_stl.y = np.array(np.array_split(
            point_cloud.T[1],
            len(point_cloud) / 3
        ))
        new_stl.z = np.array(np.array_split(
            point_cloud.T[2],
            len(point_cloud) / 3
        ))
        return StlMesh(new_stl)

    def create_figure(self):
        figure = plt.figure()
        axes = mplot3d.Axes3D(figure)

        axes.add_collection3d(
            mplot3d.art3d.Poly3DCollection(
                self.stl.vectors,
                facecolor=(0.5, 0.8, 0.5, 0.5),
                linewidth=0.5,
                edgecolor=(0, 0, 0)
            )
        )

        scale = self.stl.points.flatten()
        axes.auto_scale_xyz(scale, scale, scale)
        return figure, axes


def plot_control_points(ax, ffd):
    ax.scatter(*ffd.control_points().T, s=50, c='red')


def generate_random_stl_meshes(stl_mesh, num_samples, control_pts_per_axis, std, verbose=True):
    for i in range(num_samples):
        start_time = time.time()

        ffd_size = [control_pts_per_axis] * 3
        ffd = FFD(ffd_size)
        ffd.box_length = stl_mesh.max_point - stl_mesh.min_point + 0.1
        ffd.box_origin = stl_mesh.min_point - 0.05

        ffd.array_mu_x = np.random.normal(loc=0, scale=std, size=ffd_size)
        ffd.array_mu_y = np.random.normal(loc=0, scale=std, size=ffd_size)
        ffd.array_mu_z = np.random.normal(loc=0, scale=std, size=ffd_size)

        new_point_cloud = ffd(stl_mesh.point_cloud)

        yield stl_mesh.generate_new_from_point_cloud(new_point_cloud)
        if verbose:
            print(f'iteration {i} (out of {num_samples}) completed in {time.time() - start_time} seconds')


def main():
    stl_mesh = StlMesh.from_file(args.mesh)

    new_stl_meshes = generate_random_stl_meshes(
        stl_mesh,
        args.count,
        args.control,
        args.std
    )

    if args.demo:
        print('showing base stl')
        stl_mesh.create_figure()
        plt.show()
        for i in range(3):
            print(f'showing randomly deformed stl {i}')
            next(new_stl_meshes).create_figure()
            plt.show()

    else:
        outpath = os.path.abspath(args.outpath)
        if not os.path.exists(outpath):
            os.makedirs(outpath)

        for i, new_stl in enumerate(new_stl_meshes):
            path = os.path.join(
                os.path.abspath(outpath),
                f'result_{i}.stl'
            )
            print(path)
            new_stl.stl.save(path)


if __name__ == '__main__':
    main()
